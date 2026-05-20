# Nexus Marketplace — User Guide

**Document purpose:** End-user instructions for the Nexus Marketplace web application (Flask).  
**Audience:** Students, staff, and demo users.  
**Version:** 1.0 (aligned with the current application codebase)  
**Date:** 20 May 2026  

---

## 1. Introduction

Nexus Marketplace is a web application for buying and selling PC parts, games, and accessories, with optional **consultation** and **repair / upgrade** service requests. Users sign in with a **Nexus account**, browse the shop, pay for cart orders through **Stripe Checkout** (when configured), and manage purchases from **My Orders**. Sellers list inventory from the **Seller Dashboard**; administrators manage users and catalogue items from the **Admin** area.

This guide follows the live routes in the application (for example `/auth/register`, `/shop/search`, `/account/checkout`).

---

## 2. Getting Started: Registration and Login

### 2.1 Opening the sign-in and registration page

1. Go to the site home page (by default when running locally: `http://127.0.0.1:5000/`).
2. Click **Login / Signup** in the navigation bar (shown when you are not signed in).

You are taken to the combined authentication page:

- **URL path:** `/auth/register`  
- **On screen:** tabs for **Sign In** and **Register**.

### 2.2 Creating a new account (Register)

1. Open the **Register** tab.
2. Enter **Username**, **Email**, **Password**, and **Confirm Password**.
3. Submit the registration form.

The application checks that all fields are present, that the two passwords match, and that the username and email are not already in use. On success, your account is created with role **buyer** and status **active**. You can then switch to the **Sign In** tab and log in.

### 2.3 Signing in

1. Open the **Sign In** tab.
2. Enter **Username** and **Password** and submit.

On success, you remain on the flow that brought you to login, or you can use the site normally. The session stores your identity for cart, checkout, and account pages.

### 2.4 Signing out

- From the user menu (your username in the navbar), choose **Logout**.

You are redirected to the sign-in / register page and your session is cleared.

### 2.5 If you cannot sign in

- Confirm you are using the correct **username** (not necessarily the email address) and password.
- If the server reports that the username or email is already taken during registration, choose a different username or email.

---

## 3. For Buyers

### 3.1 Browsing and searching products

**Home page**

- The home page shows curated sections such as **Picked for you** (random active listings) and **Top trending** (popular items). Click a product card to open its detail page.

**Search**

- Use the **search** field on the home hero, or navigate so that the shop receives a search query.  
- **Browse all active products:** open search with no keywords (empty query). The catalogue lists all **active** products.  
- **Keyword search:** results match product **names** (partial match, case-insensitive).

**Categories (Shop menu)**

- Open **Shop** in the navigation bar to see category links, for example:
  - **Games**, **Accessories**
  - **CPU**, **GPU**, **Motherboard**, **Power Supplies**, **RAM**, **Storage**
  - **Prebuilt PCs**
- Category pages list **active** products in that category, with pagination where applicable.

**Product page**

- From any listing, open a product to see details, price in **GBP (£)**, stock, and (where enabled) **reviews**.

### 3.2 Shopping cart

**Requirements:** You must be **signed in** to add items to the cart.

**Adding items**

- On a product page, use the control to add the item to your cart (the site records quantity per product, up to available **stock**).

**Cart controls**

- **Navbar cart:** Open the cart icon to see a quick summary, change quantities with **−** / **+**, and open **View cart**.
- **Full cart page** (`/account/cart`): Review line items and totals, remove lines, clear the cart, or proceed toward checkout.

If a product is not **active** or has no stock, you cannot add it; the application will show an appropriate message.

### 3.3 Checkout with Stripe

**Requirements**

- Signed-in user.
- Non-empty cart.
- The server must have **Stripe** configured (`STRIPE_SECRET_KEY` in the environment). If Stripe is not configured, checkout will not proceed and a message will explain that the payment system is unavailable.

**Steps**

1. Open **Checkout** from the cart flow (`/account/checkout`).
2. Complete the **shipping details** form: full name, address, city, postcode, and country. These are stored with the order as the delivery address text.
3. Submit using **Pay with Stripe** (or the labelled submit control on the form).

The application creates a **Stripe Checkout Session** in **payment** mode, priced in **GBP**, and redirects you to Stripe’s hosted payment page. Complete payment there.

**After payment**

- On success, you are returned to the application; orders are created from the paid session, stock is reduced, and your **session cart is cleared**.
- You may see an **order confirmation** screen for the orders just created; afterwards you can use **My Orders** for a permanent list.

**If you cancel on Stripe**

- You are sent back to checkout with a cancellation notice; your cart contents remain until you change them.

**Operational note (assignments / demos):** For production-like behaviour, Stripe webhooks can be configured separately; the success return path still finalises payment when the session is **paid**.

### 3.4 Order history and order details

**Order list**

- User menu → **My Orders**, or from **My Account** → link to order history.  
- **URL path:** `/account/order-history`  
- Orders are listed newest first. Each purchase may appear as one row per seller line (the backend creates separate orders per seller line item as implemented).

**Order detail**

- Open a specific order from the list (`/account/order/<order_id>`) to see full information for that purchase.

**Cancelling an order (buyer)**

- If an order is still in **processing** delivery status, you may be able to **cancel** it from the order detail page. Cancelling restores stock for the items in that order and updates payment/delivery status in the application.  
- **Note:** Automatic Stripe refunds are **not** wired in this codebase; cancellation updates the marketplace records. Treat this as a platform-level cancellation for demos or coursework unless you extend refunds in Stripe.

### 3.5 Reviews (verified buyers)

- If you have **purchased** a product (verified in the database), you can submit a **star rating** and optional comment on that product’s page.
- You can **update** or **delete** your own review from the product page when signed in.

---

## 4. For Sellers

### 4.1 Becoming a seller (My Account)

1. Sign in as a user with role **buyer**.
2. Open **My Account** from the user menu (`/account/my-account`).
3. In the profile sidebar, click **Become a seller**.

Your role changes to **seller**. You can then use **Seller Dashboard**, **Add Product**, **My Products**, and **Orders Received** from the user menu (and the **Shop** area remains available for buying).

**Removing seller access**

- On **My Account**, if you are a **seller**, you may use **Remove seller role** to return to **buyer**. Existing listings are **not** deleted automatically; you simply cannot add new products until you become a seller again.

**Administrators**

- Users with roles **admin** or **super_admin** already satisfy seller-route checks and can access seller tools without using “Become a seller.”

### 4.2 Seller Dashboard and products

**Dashboard** (`/seller/dashboard`)

- Summary of your listings: counts and recent products.

**Add a product** (`/seller/add-product`)

- Fill in name, description, brand, price (**£**), stock quantity, category, condition, and provide **either** an **image upload** (jpg, jpeg, png, webp) **or** an **image URL**.
- Submit to create an **active** listing.

**Edit a product** (`/seller/edit-product/<product_id>`)

- Available only for products **you** own. Update fields and optionally replace the image (upload replaces stored files when applicable).

**My Products** (`/seller/my-products`)

- List view of your inventory for quick access.

**Removing your own listing**

- From seller flows that offer delete/remove, the application performs a **soft delete**: the product **status** becomes **removed** so it no longer behaves as an active shop listing.

### 4.3 Orders you sold: shipping status

1. Open **Orders Received** (`/seller/orders`).
2. Locate an order where you are the **seller**.
3. Use the provided actions to update **delivery status**:
   - **Mark as shipped** — sets status to **shipped**.
   - **Mark as delivered** — sets status to **delivered**.

These actions apply to orders assigned to you as the seller. Buyers see progress through their order history and detail views.

---

## 5. For Admins

**Access:** Only users with role **admin** or **super_admin** can open the admin area. Sign in, then use **Admin** in the navigation bar or user menu.

### 5.1 Admin Dashboard

- **URL path:** `/admin/`  
- Shows high-level counts (users, products, orders) and **recent admin activity** from the audit log.

### 5.2 User management

**User list** (`/admin/users`)

- View all users and their roles and account statuses.

**Changing role and account status**

- Use the update controls for a user to set:
  - **Role:** `buyer`, `seller`, `admin`, or `super_admin` (restrictions apply; see below).
  - **Account status:** `active`, `suspended`, or `deleted`.

**Role promotion rules**

- Only a **super_admin** can assign **admin** or **super_admin** to another user.
- A **super_admin** cannot remove their own **super_admin** role if they are the **only** remaining super admin (the system blocks this to avoid lockout).

**Editing a user’s profile**

- Admins can open the edit screen for a user to change **username** and **email**, subject to uniqueness and permission rules (regular **admin** cannot edit a **super_admin**).

**Deleting a user**

- “Delete” in the admin sense sets the user’s **account_status** to **deleted** (soft delete) and writes an admin log entry. Some combinations (for example deleting yourself or targeting a super admin) are restricted by policy in code.

**Creating admin accounts**

- **Super admins** can use **Add admin user** to create new **admin** or **super_admin** accounts with credentials.

### 5.3 Product moderation

**Product list** (`/admin/products`)

- Browse all products in the system.

**Removing a product**

- Use the remove/delete action for a product. The catalogue item is **soft-deleted** (**status** set to **removed**), and the action is **logged** in the admin audit trail.

---

## 6. Services: Consultation and Repair / Upgrade

These are **request forms**, not shopping baskets. Submissions are stored for staff to follow up (email / phone as you indicate).

### 6.1 Consultation

**How to open**

- Navigation: **Shop** → **Consultation** (category slug `consultation`).

**Form fields (summary)**

- **Full name** (required)  
- **Email** (required)  
- **Phone** (optional)  
- **What do you need help with?** — e.g. new build advice, parts recommendation / compatibility, troubleshooting, other  
- **Current setup** (optional)  
- **Goals / budget** (optional)  
- **Preferred contact method** — email, phone, or either  
- **Additional details** (required message)

Submit the form. On success you see a confirmation flash message; the request is stored in the database for processing.

### 6.2 Repair and upgrade

**How to open**

- Navigation: **Shop** → **Repair & Upgrades** (category slug `repair-upgrade`).

**Form fields (summary)**

- **Full name** and **Email** (required); **Phone** optional  
- **Service needed** — repair, upgrade, or both  
- **Device type** — desktop PC, laptop, or other  
- **Issue description or upgrade goals** (required)  
- **When do you need it?** — urgency band  
- **Preferred contact method**  
- **Additional notes** (optional)

Submit the form. A success message confirms the request was recorded.

**Signing in**

- You may submit these forms **with or without** being logged in. If you are logged in, your user id may be associated with the request for easier follow-up.

---

## 7. Quick reference: main URL paths

| Area | Typical path | Purpose |
|------|----------------|--------|
| Home | `/` | Landing, search entry, highlights |
| Sign in / Register | `/auth/register` | Login and registration |
| Logout | `/auth/logout` | End session |
| Shop search | `/shop/search` | Browse / search products |
| Product | `/shop/product/<id>` | Product detail and reviews |
| Category | `/shop/category/<slug>` | Listings or service form |
| My Account | `/account/my-account` | Profile, seller toggle |
| Cart | `/account/cart` | Full cart |
| Checkout | `/account/checkout` | Shipping form + Stripe |
| Order history | `/account/order-history` | Buyer orders |
| Seller dashboard | `/seller/dashboard` | Seller home |
| Add / edit product | `/seller/add-product`, `/seller/edit-product/<id>` | Listings |
| Seller orders | `/seller/orders` | Fulfillment status updates |
| Admin | `/admin/` | Admin home |
| Admin users / products | `/admin/users`, `/admin/products` | Moderation |

---

## 8. Glossary

| Term | Meaning |
|------|--------|
| **Active (product)** | Listed for sale with available stock rules as implemented |
| **Buyer / Seller / Admin / Super admin** | User roles controlling permissions |
| **Stripe Checkout** | Hosted payment page used for cart purchases |
| **Soft delete** | Record kept in the database but hidden from normal shop use (e.g. **removed** product, **deleted** user account status) |

---

*End of User Guide — Nexus Marketplace.*
