# Dashboard Components

This directory contains React components for the Transaction Reconciliation Dashboard.

## Components

### TransactionsTable
Displays a table of transactions with status badges and formatting.

**Props:**
- `transactions` (array): Array of transaction objects

**Features:**
- Status badges with color coding (success, pending, failed)
- Formatted transaction IDs and amounts
- Empty state handling
- Hover effects

### MismatchesTable
Displays a table of mismatches with type badges and formatted dates.

**Props:**
- `mismatches` (array): Array of mismatch objects

**Features:**
- Mismatch type badges with color coding
- Formatted dates and times
- Empty state handling
- Hover effects

### FiltersBar
Provides filtering controls for transactions and mismatches.

**Props:**
- `filters` (object): Current filter values
- `setFilters` (function): Function to update filters

**Features:**
- Date picker
- Source dropdown (core, mobile, gateway)
- Status dropdown (success, pending, failed)
- Clear filters button

## Usage Example

```jsx
import React, { useState } from 'react';
import { TransactionsTable, MismatchesTable, FiltersBar } from '../components/dashboard';
import { useTransactions, useMismatches } from '../hooks';

function Dashboard() {
  const [filters, setFilters] = useState({
    date: '',
    source: '',
    status: ''
  });

  const { transactions, loading, error } = useTransactions();
  const { mismatches } = useMismatches();

  return (
    <div>
      <FiltersBar filters={filters} setFilters={setFilters} />
      <TransactionsTable transactions={transactions} />
      <MismatchesTable mismatches={mismatches} />
    </div>
  );
}
```

## Styling

Components use Tailwind CSS classes for styling. Key design elements:
- Clean white backgrounds with subtle shadows
- Hover effects for better UX
- Color-coded status and type badges
- Responsive design with proper spacing
- Focus states for accessibility

## Data Structure

### Transaction Object
```javascript
{
  txn_id: "TXN123456",
  source: "core",
  amount: "100.00",
  status: "success",
  timestamp: "2025-12-16T10:30:00Z"
}
```

### Mismatch Object
```javascript
{
  id: "MISMATCH_001",
  txn_id: "TXN123456",
  mismatch_type: "MISSING_IN_CORE",
  detected_at: "2025-12-16T10:30:00Z",
  details: "Transaction not found in core system"
}
```