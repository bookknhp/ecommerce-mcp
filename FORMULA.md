# 📊 สูตรคำนวณ Dashboard

ตรงกับ Admin Dashboard (PHP) โดยสมบูรณ์

---

## 💰 Revenue Calculation

### Net Revenue (ยอดเงินสุทธิ)
```sql
= SUM(orders.amount_paid) 
  WHERE payment_status = 'paid' 
  AND status != 'cancelled'
```

### Gross Sales Value
```sql
= Net Revenue 
  + Total Discounts 
  + Total Points Used
```

---

## 📈 Profit Calculation

### Formula:
```
Net Profit = Net Revenue - Total Outflow

Where Total Outflow =
  + Product Cost (cost_price)
  + Marketing Cost
  + Shipping Cost
  + Operating Cost
  + Commission
  + VAT (ภาษี)
```

### Details:
```
Product Cost = SUM(oi.quantity * p.cost_price)
Marketing = SUM(oi.quantity * p.marketing_cost)
Shipping = SUM(oi.quantity * p.shipping_cost)
Operating = SUM(oi.quantity * p.operating_cost)
Commission = SUM(oi.quantity * p.commission_1)
VAT = SUM(oi.quantity * (oi.price_at_purchase * p.vat_percent / 100))
```

---

## 📊 Dashboard KPIs

| KPI | Formula |
|-----|---------|
| **ยอดรวม** | Net Revenue |
| **Order** | COUNT(orders) |
| **กำไรสุทธิ** | Net Profit |
| **Stock ต่ำ** | COUNT(products WHERE stock < 5) |

---

## ✅ ตรงกับ Admin?

- ✅ ยอดเงินสุทธิ (Net Revenue)
- ✅ ต้นทุนสินค้า (Product Cost)
- ✅ ค่าขนส่ง (Shipping)
- ✅ ค่าจัดการ (Operating)
- ✅ ค่าคนกลาง (Commission)
- ✅ ภาษี VAT
- ✅ กำไรสุทธิ (Net Profit)
- ✅ Profit Margin %

**Source:** Admin Controller Line 152-201
