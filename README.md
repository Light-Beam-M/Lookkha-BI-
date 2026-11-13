# Lookkha ลูกค้า

Tourism BI for Phuket merchants: who visits, when they come, and what to prepare next week.
All visitor figures are **mock data**, used only to demonstrate the analysis.

- `index.html`: the site, built on real Phuket open data (see below)

## ข้อมูลจริง / real data (index.html)

- `etl/build_data.py` ดึงข้อมูลจาก phuket.gdcatalog.go.th (data.go.th, สัญญาอนุญาต Open Data Common) แล้วเขียน `data/phuket-data.js`
  - dataset_10_36 ผู้โดยสารต่างชาติขาออกระหว่างประเทศ แยกสัญชาติ รายเดือน (ด่านตรวจคนเข้าเมืองท่าอากาศยานภูเก็ต)
  - dataset_10_02 ผู้โดยสารเข้า-ออกสนามบินภูเก็ต รายเดือน ในประเทศ/ระหว่างประเทศ
  - dataset_10_34 ผู้เยี่ยมเยือนรายปี ไทย/ต่างชาติ · dataset_10_09 ค่าใช้จ่ายต่อคนต่อวัน · dataset_10_08 รายได้ท่องเที่ยว
- `.github/workflows/refresh-data.yml` รันสคริปต์ทุกวันที่ 5 ของเดือน และ commit ไฟล์ข้อมูลถ้ามีการเปลี่ยนแปลง
- วิธีคำนวณ
  - **นักท่องเที่ยวรายเดือน** = ผู้โดยสารสนามบินรายเดือน (ต่างชาติ: ขาออกแยกสัญชาติ, ไทย: ขาเข้าในประเทศ) × อัตราปรับเทียบ ที่ทำให้ยอดรวมปีล่าสุดตรงกับสถิติผู้เยี่ยมเยือนทางการ
  - **รายได้** = นักท่องเที่ยว × รายได้ต่อหัว (รายได้ทางการปีล่าสุด ÷ ผู้เยี่ยมเยือนปีเดียวกัน)
  - **คาดการณ์** = เดือนเดียวกันปีก่อน × อัตราเติบโต 3 เดือนล่าสุด แยกไทย/ต่างชาติ
  - **ความแม่นยำ** วัดจากการทดสอบย้อนหลัง 1 เดือนล่วงหน้า (MAPE) ช่วงคาดการณ์ = ± MAPE × √(จำนวนเดือนล่วงหน้า)
  - **ตัวเปรียบเทียบ (benchmark)**: การเติบโตของแต่ละสัญชาติเทียบกับภาพรวมทั้งตลาด
- ข้อจำกัด: สัดส่วนรายโซนยังเป็นสมมติฐาน (ไม่มีข้อมูลรายพื้นที่) · ข้อมูลเป็นรายเดือน จึงไม่มีคำแนะนำรายสัปดาห์ · ผู้โดยสารสนามบินไม่รวมผู้ที่เดินทางทางถนนหรือทางเรือ (ปรับด้วยอัตราปรับเทียบรายปี)

Run locally: `python -m http.server 8000`, then open `http://localhost:8000/`.

Not published: `Photo/videoplayback.mp4` (raw 33 MB source, see `.gitignore`).

## วิธีคำนวณ

- **คาดการณ์ 3 เดือน**: seasonal naive ค่าเฉลี่ยของเดือนเดียวกันปีก่อน × 1.08 และ 2 ปีก่อน × 1.08²
- **สัปดาห์หน้า**: ผสมอัตรารายวันของเดือนนี้กับเดือนหน้า ตามวันที่ปัจจุบัน
- **รายได้ท่องเที่ยว** = นักท่องเที่ยว × ใช้จ่าย/คน/วัน × วันพักเฉลี่ย
- **วันฝนตก** = ปริมาณฝน ≥ 5 มม.
- **YoY** เทียบช่วงเดียวกันของปีก่อน

### หน้า "ร้านคุณควรทำอะไร" (v2)

ทุกคำตอบคำนวณตามโซนที่เลือก
- **เตรียมของสัปดาห์หน้า**: เปลี่ยนแปลงของนักท่องเที่ยวสัปดาห์หน้าเทียบสัปดาห์นี้ (±3% ถือว่าเท่าเดิม)
- **เดือนหน้า**: นักท่องเที่ยวเฉลี่ยต่อวันของเดือนหน้า (คาดการณ์) เทียบเดือนนี้
- **ภาษาป้าย/เมนู**: สัดส่วนนักท่องเที่ยวตามภาษาหลักของสัญชาติ
- **ลูกค้าที่สร้างรายได้มากสุด**: นักท่องเที่ยว × ใช้จ่ายต่อวัน × วันพัก (ไม่นับ "อื่นๆ")
- **เดือนที่ควรจ้างคนเพิ่ม / ปิดปรับปรุง**: 3 เดือนที่คนมากสุด / 2 เดือนที่คนน้อยสุด จากข้อมูลย้อนหลัง 24 เดือน

## Method

- **3-month forecast**: seasonal naive, mean of same month last year × 1.08 and two years ago × 1.08²
- **Next week**: blend of this month's and next month's daily rate by today's date
- **Tourism revenue** = visitors × spend/person/day × avg. stay
- **Rainy day** = rain ≥ 5 mm
- **YoY** compares the same period last year

### "What your shop should do" page (v2)

Every answer follows the selected zone.
- **Stock for next week**: change in visitors next week vs this week (within ±3% counts as unchanged)
- **Next month**: average daily visitors next month (forecast) vs this month
- **Sign/menu languages**: visitor share by each nationality's main language
- **Top revenue customers**: visitors × spend per day × nights stayed (excluding "Others")
- **Months to add staff / renovate**: top 3 / bottom 2 months by average visitors over 24 months of history
