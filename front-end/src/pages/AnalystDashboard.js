import React, { useState, useEffect } from 'react';
import { Container, Row, Col, Card, Button, Form, Alert } from 'react-bootstrap';
import analystService from '../services/analystService';
import { formatCurrency, formatDate, formatExportFilename } from '../utils/formatters';
import { useToast } from '../contexts/ToastContext';

/**
 * Analyst Dashboard (Tableau-style)
 * Read-only analytics, charts, and data exports
 * Available to: ANALYST role only
 * CRITICAL: ZERO write access - analysts can only view aggregate data
 */
const AnalystDashboard = () => {
  const [systemOverview, setSystemOverview] = useState(null);
  const [salesAnalytics, setSalesAnalytics] = useState(null);
  const [selectedDateRange, setSelectedDateRange] = useState('last_30_days');
  const [startDate, setStartDate] = useState('');
  const [endDate, setEndDate] = useState('');
  const [loading, setLoading] = useState(true);
  const toast = useToast();

  useEffect(() => {
    loadAnalystData();
  }, [selectedDateRange]);

  const getDateRange = () => {
    const end = new Date();
    const start = new Date();
    
    switch (selectedDateRange) {
      case 'last_7_days':
        start.setDate(start.getDate() - 7);
        break;
      case 'last_30_days':
        start.setDate(start.getDate() - 30);
        break;
      case 'last_90_days':
        start.setDate(start.getDate() - 90);
        break;
      case 'custom':
        return { start: startDate, end: endDate };
      default:
        start.setDate(start.getDate() - 30);
    }
    
    return {
      start: start.toISOString().split('T')[0],
      end: end.toISOString().split('T')[0]
    };
  };

  const loadAnalystData = async () => {
    try {
      setLoading(true);
      const dateRange = getDateRange();
      
      const [overview, sales, products, sellers, employees, customers, inventory, revenue] = await Promise.all([
        analystService.getSystemOverview(),
        analystService.getSalesAnalytics(dateRange.start, dateRange.end),
        analystService.getProductPerformance(dateRange.start, dateRange.end),
        analystService.getSellerPerformance(dateRange.start, dateRange.end),
        analystService.getEmployeeMetrics(dateRange.start, dateRange.end),
        analystService.getCustomerBehavior(dateRange.start, dateRange.end),
        analystService.getInventoryTurnover(dateRange.start, dateRange.end),
        analystService.getRevenueTrends(dateRange.start, dateRange.end),
      ]);

      setSystemOverview(overview);
      setSalesAnalytics({ sales, products, sellers, employees, customers, inventory, revenue });
    } catch (err) {
      toast.error('Failed to load analytics data');
    } finally {
      setLoading(false);
    }
  };

  const handleExport = async (dataType) => {
    try {
      const dateRange = getDateRange();
      let blob;
      
      switch (dataType) {
        case 'sales':
          blob = await analystService.exportSalesData(dateRange.start, dateRange.end);
          break;
        case 'products':
          blob = await analystService.exportProductData();
          break;
        case 'customers':
          blob = await analystService.exportCustomerData();
          break;
        default:
          return;
      }

      // Create download link
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = formatExportFilename(dataType);
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
      
      toast.success('Export completed successfully');
    } catch (err) {
      toast.error('Export failed');
    }
  };

  return (
    <Container fluid className="py-4">
      <div className="d-flex justify-content-between align-items-center mb-4">
        <div>
          <h1>📊 Analyst Dashboard</h1>
          <p className="text-muted mb-0">Tableau-style analytics and reporting</p>
        </div>
        <Alert variant="info" className="mb-0 py-2">
          <small><strong>Read-Only Access:</strong> Analytics and exports only</small>
        </Alert>
      </div>

      {/* Date Range Filter */}
      <Card className="mb-4">
        <Card.Body>
          <Row className="align-items-end">
            <Col md={3}>
              <Form.Group>
                <Form.Label><strong>Date Range</strong></Form.Label>
                <Form.Select
                  value={selectedDateRange}
                  onChange={(e) => setSelectedDateRange(e.target.value)}
                >
                  <option value="last_7_days">Last 7 Days</option>
                  <option value="last_30_days">Last 30 Days</option>
                  <option value="last_90_days">Last 90 Days</option>
                  <option value="custom">Custom Range</option>
                </Form.Select>
              </Form.Group>
            </Col>
            
            {selectedDateRange === 'custom' && (
              <>
                <Col md={2}>
                  <Form.Group>
                    <Form.Label>Start Date</Form.Label>
                    <Form.Control
                      type="date"
                      value={startDate}
                      onChange={(e) => setStartDate(e.target.value)}
                    />
                  </Form.Group>
                </Col>
                <Col md={2}>
                  <Form.Group>
                    <Form.Label>End Date</Form.Label>
                    <Form.Control
                      type="date"
                      value={endDate}
                      onChange={(e) => setEndDate(e.target.value)}
                    />
                  </Form.Group>
                </Col>
                <Col md={2}>
                  <Button variant="primary" onClick={loadAnalystData}>
                    Apply Filter
                  </Button>
                </Col>
              </>
            )}

            <Col md={3} className="ms-auto">
              <div className="d-flex gap-2 justify-content-end">
                <Button variant="outline-success" size="sm" onClick={() => handleExport('sales')}>
                  📥 Export Sales
                </Button>
                <Button variant="outline-success" size="sm" onClick={() => handleExport('products')}>
                  📥 Export Products
                </Button>
              </div>
            </Col>
          </Row>
        </Card.Body>
      </Card>

      {loading ? (
        <div className="text-center py-5">
          <div className="spinner-border text-primary" role="status">
            <span className="visually-hidden">Loading...</span>
          </div>
          <p className="mt-3 text-muted">Loading analytics...</p>
        </div>
      ) : (
        <>
          {/* System Overview Cards */}
          <h4 className="mb-3">System Overview</h4>
          <Row xs={1} md={2} lg={4} className="g-4 mb-4">
            <Col>
              <Card className="text-center h-100 border-primary">
                <Card.Body>
                  <div className="text-muted mb-2">Total Users</div>
                  <div className="display-5 fw-bold text-primary">
                    {systemOverview?.total_users?.toLocaleString() || 0}
                  </div>
                  <small className="text-success">+{systemOverview?.new_users_this_month || 0} this month</small>
                </Card.Body>
              </Card>
            </Col>
            <Col>
              <Card className="text-center h-100 border-success">
                <Card.Body>
                  <div className="text-muted mb-2">Total Orders</div>
                  <div className="display-5 fw-bold text-success">
                    {systemOverview?.total_orders?.toLocaleString() || 0}
                  </div>
                  <small className="text-muted">All time</small>
                </Card.Body>
              </Card>
            </Col>
            <Col>
              <Card className="text-center h-100 border-warning">
                <Card.Body>
                  <div className="text-muted mb-2">Total Products</div>
                  <div className="display-5 fw-bold text-warning">
                    {systemOverview?.total_products?.toLocaleString() || 0}
                  </div>
                  <small className="text-muted">Active listings</small>
                </Card.Body>
              </Card>
            </Col>
            <Col>
              <Card className="text-center h-100 border-info">
                <Card.Body>
                  <div className="text-muted mb-2">Total Revenue</div>
                  <div className="display-5 fw-bold text-info">
                    {formatCurrency(systemOverview?.total_revenue || 0)}
                  </div>
                  <small className="text-muted">All time</small>
                </Card.Body>
              </Card>
            </Col>
          </Row>

          {/* Sales Analytics */}
          <h4 className="mb-3">Sales Performance</h4>
          <Row xs={1} md={3} className="g-4 mb-4">
            <Col>
              <Card className="h-100">
                <Card.Header className="bg-light">
                  <strong>📈 Sales Metrics</strong>
                </Card.Header>
                <Card.Body>
                  <div className="mb-3">
                    <div className="text-muted">Revenue</div>
                    <div className="h4 text-success mb-0">
                      {formatCurrency(salesAnalytics?.sales?.total_revenue || 0)}
                    </div>
                  </div>
                  <div className="mb-3">
                    <div className="text-muted">Orders</div>
                    <div className="h4 mb-0">
                      {salesAnalytics?.sales?.total_orders?.toLocaleString() || 0}
                    </div>
                  </div>
                  <div>
                    <div className="text-muted">Avg Order Value</div>
                    <div className="h4 text-primary mb-0">
                      {formatCurrency(salesAnalytics?.sales?.average_order_value || 0)}
                    </div>
                  </div>
                </Card.Body>
              </Card>
            </Col>

            <Col>
              <Card className="h-100">
                <Card.Header className="bg-light">
                  <strong>📦 Product Performance</strong>
                </Card.Header>
                <Card.Body>
                  <div className="mb-3">
                    <div className="text-muted">Top Selling Product</div>
                    <div className="fw-bold">
                      {salesAnalytics?.products?.top_product?.name || 'N/A'}
                    </div>
                  </div>
                  <div className="mb-3">
                    <div className="text-muted">Products Sold</div>
                    <div className="h4 mb-0">
                      {salesAnalytics?.products?.total_sold?.toLocaleString() || 0}
                    </div>
                  </div>
                  <div>
                    <div className="text-muted">Inventory Turnover</div>
                    <div className="h4 text-warning mb-0">
                      {salesAnalytics?.inventory?.turnover_rate?.toFixed(1) || 0}x
                    </div>
                  </div>
                </Card.Body>
              </Card>
            </Col>

            <Col>
              <Card className="h-100">
                <Card.Header className="bg-light">
                  <strong>👥 Customer Insights</strong>
                </Card.Header>
                <Card.Body>
                  <div className="mb-3">
                    <div className="text-muted">Active Customers</div>
                    <div className="h4 mb-0">
                      {salesAnalytics?.customers?.active_customers?.toLocaleString() || 0}
                    </div>
                  </div>
                  <div className="mb-3">
                    <div className="text-muted">Repeat Customer Rate</div>
                    <div className="h4 text-success mb-0">
                      {salesAnalytics?.customers?.repeat_rate?.toFixed(1) || 0}%
                    </div>
                  </div>
                  <div>
                    <div className="text-muted">Avg Customer Value</div>
                    <div className="h4 text-primary mb-0">
                      {formatCurrency(salesAnalytics?.customers?.lifetime_value || 0)}
                    </div>
                  </div>
                </Card.Body>
              </Card>
            </Col>
          </Row>

          {/* Seller & Employee Performance */}
          <Row xs={1} md={2} className="g-4 mb-4">
            <Col>
              <Card className="h-100">
                <Card.Header className="bg-light">
                  <strong>🏪 Seller Performance</strong>
                </Card.Header>
                <Card.Body>
                  <div className="mb-3">
                    <div className="text-muted">Active Sellers</div>
                    <div className="h4 mb-0">
                      {salesAnalytics?.sellers?.active_sellers || 0}
                    </div>
                  </div>
                  <div className="mb-3">
                    <div className="text-muted">Top Seller</div>
                    <div className="fw-bold">
                      {salesAnalytics?.sellers?.top_seller?.business_name || 'N/A'}
                    </div>
                  </div>
                  <div>
                    <div className="text-muted">Avg Seller Rating</div>
                    <div className="h4 text-warning mb-0">
                      ⭐ {salesAnalytics?.sellers?.average_rating?.toFixed(1) || 0}
                    </div>
                  </div>
                </Card.Body>
              </Card>
            </Col>

            <Col>
              <Card className="h-100">
                <Card.Header className="bg-light">
                  <strong>👔 Employee Metrics</strong>
                </Card.Header>
                <Card.Body>
                  <div className="mb-3">
                    <div className="text-muted">Total Employees</div>
                    <div className="h4 mb-0">
                      {salesAnalytics?.employees?.total_employees || 0}
                    </div>
                  </div>
                  <div className="mb-3">
                    <div className="text-muted">Avg Hours/Week</div>
                    <div className="h4 mb-0">
                      {salesAnalytics?.employees?.avg_hours_per_week?.toFixed(1) || 0}h
                    </div>
                  </div>
                  <div>
                    <div className="text-muted">Payroll Total</div>
                    <div className="h4 text-success mb-0">
                      {formatCurrency(salesAnalytics?.employees?.total_payroll || 0)}
                    </div>
                  </div>
                </Card.Body>
              </Card>
            </Col>
          </Row>

          {/* Chart Placeholder */}
          <Card className="mb-4">
            <Card.Header className="bg-light">
              <strong>📊 Revenue Trends</strong>
            </Card.Header>
            <Card.Body>
              <div className="text-center py-5 bg-light rounded">
                <div style={{ fontSize: '3rem' }}>📈</div>
                <p className="text-muted mt-3">
                  Chart visualization would go here<br />
                  <small>(Integrate with Chart.js or Recharts)</small>
                </p>
              </div>
            </Card.Body>
          </Card>

          {/* Export Actions */}
          <Card>
            <Card.Header className="bg-light">
              <strong>📥 Data Exports</strong>
            </Card.Header>
            <Card.Body>
              <div className="d-flex gap-3 flex-wrap">
                <Button variant="outline-primary" onClick={() => handleExport('sales')}>
                  📊 Export Sales Data (CSV)
                </Button>
                <Button variant="outline-primary" onClick={() => handleExport('products')}>
                  📦 Export Product Data (CSV)
                </Button>
                <Button variant="outline-primary" onClick={() => handleExport('customers')}>
                  👥 Export Customer Data (CSV)
                </Button>
                <Button variant="outline-secondary" onClick={loadAnalystData}>
                  🔄 Refresh Data
                </Button>
              </div>
            </Card.Body>
          </Card>
        </>
      )}
    </Container>
  );
};

export default AnalystDashboard;
