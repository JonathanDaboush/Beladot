import React from 'react';
import PageHeader from '../components/PageHeader';

export default function AssistancePage() {
  const action = (
    <a className="btn" href="/catalog">Browse Help Topics</a>
  );
  return (
    <div className="page">
      <PageHeader title="Help & Customer Assistance" subtitle="We're here to help with orders, returns, and account questions" action={action} />
      <div className="section">
        <div className="card" style={{ padding: '1rem' }}>
          <h2 className="h5" style={{ marginTop: 0 }}>Contact Us</h2>
          <p className="muted">Reach our support team via phone or email. Typical response times are under 24 hours.</p>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
            <div className="contact-block">
              <div className="label muted">Phone</div>
              <div className="value h6">1-800-555-0199</div>
              <div className="desc">Available 7 days a week · 6am–10pm PT</div>
            </div>
            <div className="contact-block">
              <div className="label muted">Email</div>
              <div className="value h6">support@bela-commerce.example</div>
              <div className="desc">We reply within one business day</div>
            </div>
          </div>
        </div>
      </div>

      <div className="section">
        <div className="card" style={{ padding: '1rem' }}>
          <h2 className="h5" style={{ marginTop: 0 }}>Popular Topics</h2>
          <ul className="link-list">
            <li><a href="/orders">Track my order</a></li>
            <li><a href="/profile">Update my address</a></li>
            <li><a href="/wishlist">Manage my wishlist</a></li>
            <li><a href="/forgot-password">Reset my password</a></li>
            <li><a href="/catalog">Browse categories</a></li>
          </ul>
        </div>
      </div>

      <div className="section">
        <div className="card" style={{ padding: '1rem' }}>
          <h2 className="h5" style={{ marginTop: 0 }}>FAQs</h2>
          <div className="faq">
            <div className="faq-item">
              <div className="question h6">How do I return an item?</div>
              <div className="answer">Start a return from your Order History page. Follow the prompts to print a return label. Most items can be returned within 30 days.</div>
            </div>
            <div className="faq-item">
              <div className="question h6">Where is my package?</div>
              <div className="answer">Go to Orders to view shipment status and tracking details. If you need more help, call us at 1-800-555-0199.</div>
            </div>
            <div className="faq-item">
              <div className="question h6">How do I update my payment method?</div>
              <div className="answer">Visit your Profile / Account page and update payment info under Billing.</div>
            </div>
            <div className="faq-item">
              <div className="question h6">Do you have weekend support?</div>
              <div className="answer">Yes. Our phone support is available every day, 6am–10pm Pacific Time.</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
