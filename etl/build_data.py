"""Download Phuket tourism open data (data.go.th / phuket.gdcatalog.go.th) and write data/phuket-data.js.

Run:  python etl/build_data.py            (writes data/phuket-data.js next to the site)
Uses the standard library only so GitHub Actions can run it without installs.
All sources: Phuket Provincial Tourism and Sports Office / AOT Phuket, licence "Open Data Common".
"""
import csv, io, json, sys, urllib.request
from collections import defaultdict
from datetime import date
from pathlib import Path

CATALOG = 'https://phuket.gdcatalog.go.th'
BASE = CATALOG + '/dataset/'
# key: (dataset name, Thai title, English title, CSV url or list of urls)
SOURCES = {
    'visitors': ('dataset_10_34', 'ผู้เยี่ยมเยือน นักท่องเที่ยว และนักทัศนาจร (รายปี)', 'Visitors, tourists and excursionists (yearly)',
                 BASE + '49a74f22-f8c0-4a96-bf12-f7a07ce3217d/resource/712abaca-5fbc-4e4c-9fc7-e793447fa00c/download/dataset_10_34_-.csv'),
    'spend': ('dataset_10_09', 'ค่าใช้จ่ายเฉลี่ยต่อคนต่อวัน (รายปี)', 'Average spend per person per day (yearly)',
              BASE + 'dc04c36d-a855-4086-af14-1e657920f98d/resource/b988668c-65a9-4b38-935e-368c90a0c735/download/dataset_10_09_-.csv'),
    'revenue': ('dataset_10_08', 'รายได้จากการท่องเที่ยว ชาวไทย-ชาวต่างชาติ (รายปี)', 'Tourism revenue, Thai and foreign (yearly)',
                BASE + '0e103d7e-f7f7-4d2c-b17d-9d07b7e41bba/resource/e86310b0-3b57-4cec-90b3-4c4e6c927494/download/untitled.csv'),
    'airport': ('dataset_10_02', 'ผู้โดยสารเข้า-ออกสนามบินภูเก็ต (รายเดือน)', 'Phuket airport passengers in and out (monthly)',
                BASE + 'd5951e6e-0b7a-4905-b04e-64882701acf9/resource/1a936cf3-2e43-452d-8a27-298fc22a016e/download/untitled.csv'),
    'nat': ('dataset_10_36', 'ผู้โดยสารชาวต่างชาติขาออก ระหว่างประเทศ แยกสัญชาติ (รายเดือน)', 'Foreign international departures by nationality (monthly)', [
        BASE + '02020898-1cd0-4f86-8f4c-7f523dc76e45/resource/2502347c-3151-4d12-bb02-b166031b3f2e/download/dataset_10_36_-.csv',
        BASE + '02020898-1cd0-4f86-8f4c-7f523dc76e45/resource/305cebc0-bb2b-4890-aa53-e3cb334ab645/download/dataset_10_36_-.csv',
        BASE + '02020898-1cd0-4f86-8f4c-7f523dc76e45/resource/b28cc0c6-4272-4ab9-9a3e-a4892fcd84a7/download/untitled.csv']),
}
MONTH_TH = ['มกราคม', 'กุมภาพันธ์', 'มีนาคม', 'เมษายน', 'พฤษภาคม', 'มิถุนายน',
            'กรกฎาคม', 'สิงหาคม', 'กันยายน', 'ตุลาคม', 'พฤศจิกายน', 'ธันวาคม']
# nationality as written in the source -> code, Thai/English name, main language (Thai/English)
COUNTRY = {
    'สหพันธรัฐรัสเซีย': ('RU', 'รัสเซีย', 'Russia', 'รัสเซีย', 'Russian'),
    'สาธารณรัฐประชาชนจีน': ('CN', 'จีน', 'China', 'จีน', 'Chinese'),
    'สาธารณรัฐอินเดีย': ('IN', 'อินเดีย', 'India', 'อังกฤษ', 'English'),
    'ออสเตรเลีย': ('AU', 'ออสเตรเลีย', 'Australia', 'อังกฤษ', 'English'),
    'สหราชอาณาจักร': ('GB', 'สหราชอาณาจักร', 'UK', 'อังกฤษ', 'English'),
    'สหพันธสาธารณรัฐเยอรมันนี': ('DE', 'เยอรมนี', 'Germany', 'เยอรมัน', 'German'),
    'สาธารณรัฐฝรั่งเศส': ('FR', 'ฝรั่งเศส', 'France', 'ฝรั่งเศส', 'French'),
    'มาเลเซีย': ('MY', 'มาเลเซีย', 'Malaysia', 'มลายู', 'Malay'),
    'สาธารณรัฐเกาหลี': ('KR', 'เกาหลีใต้', 'South Korea', 'เกาหลี', 'Korean'),
    'สหรัฐอเมริกา': ('US', 'สหรัฐอเมริกา', 'USA', 'อังกฤษ', 'English'),
    'สาธารณรัฐคาซัคสถาน': ('KZ', 'คาซัคสถาน', 'Kazakhstan', 'รัสเซีย', 'Russian'),
    'รัฐอิสราเอล': ('IL', 'อิสราเอล', 'Israel', 'ฮีบรู', 'Hebrew'),
    'ราชอาณาจักรซาอุดีอาระเบีย': ('SA', 'ซาอุดีอาระเบีย', 'Saudi Arabia', 'อาหรับ', 'Arabic'),
    'สาธารณรัฐสิงคโปร์': ('SG', 'สิงคโปร์', 'Singapore', 'อังกฤษ', 'English'),
    'ญี่ปุ่น': ('JP', 'ญี่ปุ่น', 'Japan', 'ญี่ปุ่น', 'Japanese'),
}
TOP_N = 8
SKIP_NAT = {'รวม', 'ราชอาณาจักรไทย'}  # the total row, and Thai nationals (counted as domestic)


def fetch(url):
    with urllib.request.urlopen(urllib.request.Request(url, headers={'User-Agent': 'lookkha-etl'}), timeout=120) as r:
        return list(csv.reader(io.StringIO(r.read().decode('utf-8-sig'))))


def publisher(name):
    """Publishing organisation as listed in the catalogue; the host name if the lookup fails."""
    try:
        with urllib.request.urlopen(f'{CATALOG}/api/3/action/package_show?id={name}', timeout=60) as r:
            return json.load(r)['result']['organization']['title']
    except Exception as e:  # metadata is nice-to-have, never block the data refresh on it
        print(f'warning: no publisher for {name}: {e}', file=sys.stderr)
        return 'phuket.gdcatalog.go.th'


def num(s):
    s = (s or '').replace(',', '').strip()
    try:
        return float(s)
    except ValueError:  # e.g. "รอประมวลผล" (still processing)
        return None


def by_year(rows, value_col, nat_col, type_col=None, want_type=None):
    """{year_ce: {'th': x, 'fo': y}} from the yearly Thai/foreign tables."""
    hdr, out = rows[0], defaultdict(dict)
    for r in rows[1:]:
        if type_col is not None and r[type_col] != want_type:
            continue
        seg = {'ชาวไทย': 'th', 'ชาวต่างชาติ': 'fo'}.get(r[nat_col])
        v = num(r[value_col])
        if seg and v is not None:
            out[int(r[1]) - 543][seg] = v
    assert out, f'no rows parsed from {hdr}'
    return {y: d for y, d in sorted(out.items()) if len(d) == 2}


def main(out_path):
    vis = by_year(fetch(SOURCES['visitors'][3]), 5, 4, 3, 'ผู้เยี่ยมเยือน')
    spend = by_year(fetch(SOURCES['spend'][3]), 5, 4, 3, 'ผู้เยี่ยมเยือน')
    rev = by_year(fetch(SOURCES['revenue'][3]), 4, 3)

    air = defaultdict(dict)  # monthly arrivals ('เข้า'), domestic vs international
    for r in fetch(SOURCES['airport'][3])[1:]:
        if r[5] == 'เข้า' and r[4] in ('ภายในประเทศ', 'ระหว่างประเทศ') and r[2] in MONTH_TH:
            air[(int(r[1]) - 543, MONTH_TH.index(r[2]))]['dom' if r[4] == 'ภายในประเทศ' else 'intl'] = num(r[6])
    air = {k: v for k, v in air.items() if len(v) == 2 and None not in v.values()}

    nat = defaultdict(lambda: defaultdict(float))  # (y, m) -> country -> departures
    for url in SOURCES['nat'][3]:
        for r in fetch(url)[1:]:
            if r[1] not in MONTH_TH:
                continue
            name = r[2].split('/')[0].strip()
            v = num(r[3])
            if name not in SKIP_NAT and v:
                nat[(int(r[0]) - 543, MONTH_TH.index(r[1]))][name] += v

    latest = min(max(air), max(nat))  # last month present in both monthly sources
    last12 = sorted(k for k in nat if k <= latest)[-12:]
    rank = defaultdict(float)
    for k in last12:
        for n, v in nat[k].items():
            rank[n] += v
    top = [n for n, _ in sorted(rank.items(), key=lambda x: -x[1])[:TOP_N]]
    meta = {n: COUNTRY.get(n, (f'X{i}', n, n, 'อังกฤษ', 'English')) for i, n in enumerate(top)}
    codes = [meta[n][0] for n in top] + ['OT']
    series = []
    for (y, m) in sorted(nat):
        if (y, m) > latest:
            continue
        row = nat[(y, m)]
        vals = [row.get(n, 0.0) for n in top]
        vals.append(sum(row.values()) - sum(vals))
        series.append({'y': y, 'm': m, 'v': [round(x) for x in vals]})

    data = {
        'fetched': date.today().isoformat(),
        'latest': {'y': latest[0], 'm': latest[1]},
        # page = the dataset's catalogue page (human-readable), not the raw CSV download
        'sources': [{'id': s[0], 'title': [s[1], s[2]], 'org': publisher(s[0]), 'page': BASE + s[0]} for s in SOURCES.values()],
        'annual': {y: {k: round(v) for k, v in d.items()} for y, d in vis.items()},
        'spend': spend,
        'revenue': rev,  # million baht
        'airport': [{'y': y, 'm': m, 'dom': round(d['dom']), 'intl': round(d['intl'])} for (y, m), d in sorted(air.items()) if (y, m) <= latest],
        'nat': {'codes': codes,
                'names': {meta[n][0]: [meta[n][1], meta[n][2]] for n in top},
                'lang': {meta[n][0]: [meta[n][3], meta[n][4]] for n in top},
                'series': series},
    }
    # sanity checks: refuse to publish a broken file
    assert len(data['airport']) >= 13 and len(series) >= 13, 'need at least 13 months for year-on-year'
    assert all(len(s['v']) == TOP_N + 1 for s in series)
    assert max(vis) >= latest[0] - 1, 'yearly visitor table is more than a year behind the monthly data'
    Path(out_path).parent.mkdir(parents=True, exist_ok=True)
    Path(out_path).write_text('// generated by etl/build_data.py, do not edit\nwindow.PHUKET_DATA=' +
                              json.dumps(data, ensure_ascii=False, separators=(',', ':')) + ';\n', encoding='utf-8')
    print(f'wrote {out_path}: latest {latest[0]}-{latest[1] + 1:02d}, top {codes}, {len(series)} nat months, {len(data["airport"])} airport months')


if __name__ == '__main__':
    main(sys.argv[1] if len(sys.argv) > 1 else str(Path(__file__).resolve().parent.parent / 'data' / 'phuket-data.js'))
