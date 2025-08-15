Stripe Setup (Test Mode)
========================

1) Create products and prices in Stripe Dashboard:
   - Product: "Predictions Access"
     Prices:
       - Monthly
       - Quarterly
       - Yearly

2) Obtain keys (Developers > API keys):
   STRIPE_SECRET_KEY=sk_test_...
   (put in api/.env)

3) Webhooks:
   - Add endpoint: https://<your-backend-domain>/webhooks/stripe
   - Listen to:
       checkout.session.completed
       customer.subscription.updated
       customer.subscription.deleted
       invoice.payment_failed
   - Save STRIPE_WEBHOOK_SECRET in api/.env

4) Local testing:
   stripe listen --forward-to localhost:8080/webhooks/stripe
