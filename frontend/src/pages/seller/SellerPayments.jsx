// Moved from src/seller
import React, { useState } from 'react';
import './SellerPayments.css';
import Button from '../../components/Button';
import PageHeader from '../../components/PageHeader';

export default function SellerPayments() {
  const [year, setYear] = useState('');
  const [month, setMonth] = useState('');
  const [payouts, setPayouts] = useState([]);

  const handleSearch = () => {
    // TODO: Fetch payouts for year/month
  };

  return (
    <div className="seller-payments-page">
      <PageHeader title="Payouts" subtitle="View monthly payout summaries and transfers" />
      <div className="payout-controls">
        <input type="number" placeholder="Year" value={year} onChange={e => setYear(e.target.value)} />
        <input type="number" placeholder="Month" value={month} onChange={e => setMonth(e.target.value)} />
        <Button kind="primary" onClick={handleSearch}>View Payouts</Button>
      </div>
      <div className="payout-list">
        {payouts.map((payout, idx) => (
          <div key={idx} className="payout-card">
            {Object.entries(payout).map(([key, value]) => (
              key !== 'payout_id' && key !== 'seller_id' ? <div key={key}><b>{key}:</b> {value}</div> : null
            ))}
          </div>
        ))}
      </div>
    </div>
  );
}
