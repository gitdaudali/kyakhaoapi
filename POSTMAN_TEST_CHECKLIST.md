# ✅ FAQ Module - Postman Testing Checklist

## 🚀 Quick Start

### Step 1: Start Your Server
```powershell
uvicorn main:app --reload
```
✅ Server running at: `http://localhost:8000`

---

## 📝 ADMIN TESTING (Requires Token)

### ✅ 1. Get Admin Token
```
POST http://localhost:8000/api/v1/auth/login

Body:
{
  "email": "your_admin_email",
  "password": "your_admin_password"
}
```
**Save the `access_token`** ← You'll need this!

---

### ✅ 2. Create FAQ #1 (Account Management)
```
POST http://localhost:8000/api/v1/admin/faq/

Headers:
Authorization: Bearer YOUR_TOKEN_HERE
Content-Type: application/json

Body:
{
  "question": "How do I reset my password?",
  "answer": "Go to login page, click 'Forgot Password', enter your email, and follow the OTP instructions.",
  "category": "Account Management",
  "is_active": true,
  "is_featured": true,
  "sort_order": 1
}
```
✅ Status: 201 Created
📝 **Save the `id` from response**

---

### ✅ 3. Create FAQ #2 (Billing)
```
POST http://localhost:8000/api/v1/admin/faq/

Headers:
Authorization: Bearer YOUR_TOKEN_HERE
Content-Type: application/json

Body:
{
  "question": "What payment methods do you accept?",
  "answer": "We accept Visa, MasterCard, American Express, PayPal, and bank transfers.",
  "category": "Billing & Payments",
  "is_active": true,
  "is_featured": false,
  "sort_order": 2
}
```
✅ Status: 201 Created

---

### ✅ 4. Create FAQ #3 (Streaming)
```
POST http://localhost:8000/api/v1/admin/faq/

Headers:
Authorization: Bearer YOUR_TOKEN_HERE
Content-Type: application/json

Body:
{
  "question": "What video quality is available?",
  "answer": "We offer 480p, 720p HD, 1080p Full HD, and 4K Ultra HD streaming.",
  "category": "Content & Streaming",
  "is_active": true,
  "is_featured": true,
  "sort_order": 3
}
```
✅ Status: 201 Created

---

### ✅ 5. Get All FAQs (Admin View)
```
GET http://localhost:8000/api/v1/admin/faq/

Headers:
Authorization: Bearer YOUR_TOKEN_HERE
```
✅ Should return all 3 FAQs

---

### ✅ 6. Update FAQ
```
PUT http://localhost:8000/api/v1/admin/faq/YOUR_FAQ_ID

Headers:
Authorization: Bearer YOUR_TOKEN_HERE
Content-Type: application/json

Body:
{
  "question": "How can I reset my password?",
  "is_featured": true
}
```
✅ Status: 200 OK

---

### ✅ 7. Toggle Active Status
```
PATCH http://localhost:8000/api/v1/admin/faq/YOUR_FAQ_ID/toggle-active

Headers:
Authorization: Bearer YOUR_TOKEN_HERE
```
✅ Should toggle is_active true/false

---

### ✅ 8. Toggle Featured Status
```
PATCH http://localhost:8000/api/v1/admin/faq/YOUR_FAQ_ID/toggle-featured

Headers:
Authorization: Bearer YOUR_TOKEN_HERE
```
✅ Should toggle is_featured true/false

---

## 👥 USER TESTING (No Token Required)

### ✅ 9. Get All Categories
```
GET http://localhost:8000/api/v1/faq/categories/list
```
✅ Should return:
```json
{
  "categories": [
    "Account Management",
    "Billing & Payments",
    "Content & Streaming"
  ]
}
```

---

### ✅ 10. Get FAQs by Category - Account Management
```
GET http://localhost:8000/api/v1/faq/?category=Account Management
```
✅ Should return FAQ #1 only

---

### ✅ 11. Get FAQs by Category - Billing
```
GET http://localhost:8000/api/v1/faq/?category=Billing & Payments
```
✅ Should return FAQ #2 only

---

### ✅ 12. Get FAQs by Category - Streaming
```
GET http://localhost:8000/api/v1/faq/?category=Content & Streaming
```
✅ Should return FAQ #3 only

---

### ✅ 13. Get All Active FAQs
```
GET http://localhost:8000/api/v1/faq/
```
✅ Should return all active FAQs

---

### ✅ 14. Get Featured FAQs Only
```
GET http://localhost:8000/api/v1/faq/featured/list
```
✅ Should return only featured FAQs

---

### ✅ 15. Search FAQs
```
GET http://localhost:8000/api/v1/faq/?search=password
```
✅ Should return FAQs containing "password"

---

### ✅ 16. Get Single FAQ by ID
```
GET http://localhost:8000/api/v1/faq/YOUR_FAQ_ID
```
✅ Should return FAQ and increment view_count

---

## 🔙 ADMIN DELETE TEST

### ✅ 17. Delete FAQ
```
DELETE http://localhost:8000/api/v1/admin/faq/YOUR_FAQ_ID

Headers:
Authorization: Bearer YOUR_TOKEN_HERE
```
✅ Status: 200 OK
✅ Message: "FAQ deleted successfully"

---

### ✅ 18. Verify Deleted FAQ Not in User View
```
GET http://localhost:8000/api/v1/faq/
```
✅ Deleted FAQ should NOT appear in list

---

## 📊 Expected Results Summary

| Test | Endpoint | Expected |
|------|----------|----------|
| Create FAQ | POST /admin/faq/ | 201 Created ✅ |
| Get All (Admin) | GET /admin/faq/ | 200 OK, all FAQs ✅ |
| Update FAQ | PUT /admin/faq/{id} | 200 OK ✅ |
| Delete FAQ | DELETE /admin/faq/{id} | 200 OK ✅ |
| Get Categories | GET /faq/categories/list | List of categories ✅ |
| Filter by Category | GET /faq/?category=X | Only category X ✅ |
| Featured FAQs | GET /faq/featured/list | Only featured ✅ |
| Search | GET /faq/?search=X | Matching FAQs ✅ |

---

## 🎯 Main Requirement Verified

**✅ Admin creates FAQ: Question → Answer → Category**
**✅ User gets FAQs filtered by Category**

---

## 📖 Full Documentation

- **Complete Guide**: `FAQ_POSTMAN_GUIDE.md`
- **Implementation Details**: `FAQ_IMPLEMENTATION_SUMMARY.md`
- **Quick Reference**: `POSTMAN_QUICK_REFERENCE.md`

---

## 🌐 View API Docs

Open in browser:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

---

## ✅ All Tests Passed?

If all checkboxes are ✅, your FAQ module is **working perfectly**! 🎉

---

## 🆘 Need Help?

**Common Issues**:

1. **401 Unauthorized**: Make sure you're using `Authorization: Bearer YOUR_TOKEN`
2. **404 Not Found**: Check the endpoint URL is correct
3. **422 Validation Error**: Check request body format matches examples
4. **500 Server Error**: Check server logs for details

**Check Server Logs**: Look at your terminal where uvicorn is running

---

**Happy Testing!** 🚀

