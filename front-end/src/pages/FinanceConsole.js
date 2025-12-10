import React, { useState, useEffect } from 'react';
import { Container, Row, Col, Card, Table, Button, Badge, Nav, Form, Modal, Alert } from 'react-bootstrap';
import financeService from '../services/financeService';
import { TableSkeleton } from '../components/common/LoadingSkeleton';
import { EmptyEmployeesState } from '../components/common/EmptyState';
import { useKeyboardShortcuts, SHORTCUTS } from '../utils/keyboardShortcuts';
import { formatCurrency, formatDate, formatHoursWorked } from '../utils/formatters';
import { useToast } from '../contexts/ToastContext';

/**
 * Finance Console (QuickBooks-style)
 * Payroll management, revenue reports, employee financial records
 * Available to: FINANCE, FINANCE_MANAGER roles only
 * CRITICAL: NO product or inventory access (department boundary)
 */
const FinanceConsole = () => {
  const [activeTab, setActiveTab] = useState('payroll');
  const [employees, setEmployees] = useState([]);
  const [payrollData, setPayrollData] = useState([]);
  const [revenueReport, setRevenueReport] = useState(null);
  const [selectedEmployee, setSelectedEmployee] = useState(null);
  const [showPayrollModal, setShowPayrollModal] = useState(false);
  const [loading, setLoading] = useState(true);
  const toast = useToast();

  // Keyboard shortcuts
  const shortcuts = [
    { ...SHORTCUTS.FINANCE.PAYROLL, callback: () => setActiveTab('payroll') },
    { ...SHORTCUTS.FINANCE.REPORTS, callback: () => setActiveTab('reports') },
  ];
  useKeyboardShortcuts(shortcuts, []);

  useEffect(() => {
    loadFinanceData();
  }, [activeTab]);

  const loadFinanceData = async () => {
    try {
      setLoading(true);
      if (activeTab === 'payroll') {
        const data = await financeService.getEmployeePayrollData();
        setPayrollData(data.items || data || []);
      } else if (activeTab === 'employees') {
        const data = await financeService.getEmployeeList();
        setEmployees(data.items || data || []);
      } else if (activeTab === 'reports') {
        const [revenue, profitLoss] = await Promise.all([
          financeService.getRevenueReport(),
          financeService.getProfitLossReport(),
        ]);
        setRevenueReport({ ...revenue, ...profitLoss });
      }
    } catch (err) {
      toast.error('Failed to load finance data');
    } finally {
      setLoading(false);
    }
  };

  const handleCalculatePayroll = async (employeeId) => {
    try {
      const result = await financeService.calculatePayroll(employeeId);
      toast.success(`Payroll calculated: ${formatCurrency(result.total_pay)}`);
      loadFinanceData();
    } catch (err) {
      toast.error('Failed to calculate payroll');
    }
  };

  const handleIssueBonus = async (employeeId, amount, reason) => {
    try {
      await financeService.issueBonus(employeeId, amount, reason);
      toast.success('Bonus issued successfully');
      loadFinanceData();
    } catch (err) {
      toast.error('Failed to issue bonus');
    }
  };

  const renderPayrollTab = () => (
    <div>
      <div className="d-flex justify-content-between align-items-center mb-3">
        <h4>Payroll Approval Queue</h4>
        <Button variant="primary" onClick={() => handleCalculatePayroll('all')}>
          Calculate All Payroll
        </Button>
      </div>

      {loading ? (
        <TableSkeleton rows={10} />
      ) : payrollData.length === 0 ? (
        <EmptyEmployeesState message="No payroll data available" />
      ) : (
        <Card>
          <Table responsive hover className="mb-0">
            <thead className="table-light">
              <tr>
                <th>Employee</th>
                <th>Hours Worked</th>
                <th>Hourly Rate</th>
                <th>Gross Pay</th>
                <th>Deductions</th>
                <th>Net Pay</th>
                <th>Status</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {payrollData.map((payroll) => (
                <tr key={payroll.id}>
                  <td>
                    <strong>{payroll.employee_name}</strong>
                    <br />
                    <small className="text-muted">{payroll.employee_email}</small>
                  </td>
                  <td>{formatHoursWorked(payroll.hours_worked || 0)}</td>
                  <td>{formatCurrency(payroll.hourly_rate || 0)}</td>
                  <td><strong>{formatCurrency(payroll.gross_pay || 0)}</strong></td>
                  <td>{formatCurrency(payroll.deductions || 0)}</td>
                  <td className="text-success">
                    <strong>{formatCurrency(payroll.net_pay || 0)}</strong>
                  </td>
                  <td>
                    {payroll.status === 'APPROVED' ? (
                      <Badge bg="success">Approved</Badge>
                    ) : payroll.status === 'PENDING' ? (
                      <Badge bg="warning">Pending</Badge>
                    ) : (
                      <Badge bg="secondary">Draft</Badge>
                    )}
                  </td>
                  <td>
                    <Button
                      variant="link"
                      size="sm"
                      className="p-0 me-2"
                      onClick={() => {
                        setSelectedEmployee(payroll);
                        setShowPayrollModal(true);
                      }}
                    >
                      💰 Process
                    </Button>
                  </td>
                </tr>
              ))}
            </tbody>
          </Table>
        </Card>
      )}
    </div>
  );

  const renderEmployeesTab = () => (
    <div>
      <h4 className="mb-3">Employee Financial Records</h4>
      
      {loading ? (
        <TableSkeleton rows={10} />
      ) : employees.length === 0 ? (
        <EmptyEmployeesState />
      ) : (
        <Card>
          <Table responsive hover className="mb-0">
            <thead className="table-light">
              <tr>
                <th>Employee</th>
                <th>Department</th>
                <th>Hire Date</th>
                <th>Salary/Rate</th>
                <th>YTD Earnings</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {employees.map((employee) => (
                <tr key={employee.id}>
                  <td>
                    <strong>{employee.first_name} {employee.last_name}</strong>
                    <br />
                    <small className="text-muted">{employee.email}</small>
                  </td>
                  <td><Badge bg="info">{employee.department}</Badge></td>
                  <td>{formatDate(employee.hire_date)}</td>
                  <td>{formatCurrency(employee.salary || employee.hourly_rate || 0)}</td>
                  <td className="text-success">
                    <strong>{formatCurrency(employee.ytd_earnings || 0)}</strong>
                  </td>
                  <td>
                    <Button variant="link" size="sm" className="p-0">
                      📄 View Details
                    </Button>
                  </td>
                </tr>
              ))}
            </tbody>
          </Table>
        </Card>
      )}
    </div>
  );

  const renderReportsTab = () => (
    <div>
      <h4 className="mb-4">Financial Reports</h4>

      {loading ? (
        <div>Loading reports...</div>
      ) : (
        <>
          {/* Summary Cards */}
          <Row xs={1} md={2} lg={4} className="g-4 mb-4">
            <Col>
              <Card className="text-center h-100 border-success">
                <Card.Body>
                  <div className="text-muted mb-2">Total Revenue</div>
                  <div className="display-6 fw-bold text-success">
                    {formatCurrency(revenueReport?.total_revenue || 0)}
                  </div>
                  <small className="text-success">This Period</small>
                </Card.Body>
              </Card>
            </Col>
            <Col>
              <Card className="text-center h-100 border-danger">
                <Card.Body>
                  <div className="text-muted mb-2">Total Expenses</div>
                  <div className="display-6 fw-bold text-danger">
                    {formatCurrency(revenueReport?.total_expenses || 0)}
                  </div>
                  <small className="text-muted">Operating Costs</small>
                </Card.Body>
              </Card>
            </Col>
            <Col>
              <Card className="text-center h-100 border-primary">
                <Card.Body>
                  <div className="text-muted mb-2">Net Profit</div>
                  <div className="display-6 fw-bold text-primary">
                    {formatCurrency(revenueReport?.net_profit || 0)}
                  </div>
                  <small className="text-muted">After All Costs</small>
                </Card.Body>
              </Card>
            </Col>
            <Col>
              <Card className="text-center h-100 border-warning">
                <Card.Body>
                  <div className="text-muted mb-2">Payroll</div>
                  <div className="display-6 fw-bold text-warning">
                    {formatCurrency(revenueReport?.payroll_total || 0)}
                  </div>
                  <small className="text-muted">Employee Costs</small>
                </Card.Body>
              </Card>
            </Col>
          </Row>

          {/* Actions */}
          <Card>
            <Card.Header className="bg-light">
              <strong>Export Reports</strong>
            </Card.Header>
            <Card.Body>
              <div className="d-flex gap-2 flex-wrap">
                <Button variant="outline-primary">📊 Export Revenue Report</Button>
                <Button variant="outline-primary">📈 Export P&L Statement</Button>
                <Button variant="outline-primary">💼 Export Payroll Summary</Button>
                <Button variant="outline-primary">🧾 Generate Tax Documents</Button>
              </div>
            </Card.Body>
          </Card>
        </>
      )}
    </div>
  );

  return (
    <Container fluid className="py-4">
      <div className="d-flex justify-content-between align-items-center mb-4">
        <div>
          <h1>💼 Finance Console</h1>
          <p className="text-muted mb-0">QuickBooks-style financial management</p>
        </div>
        <Alert variant="info" className="mb-0 py-2">
          <small><strong>Department Boundary:</strong> No product/inventory access</small>
        </Alert>
      </div>

      {/* Navigation Tabs */}
      <Nav variant="tabs" className="mb-4">
        <Nav.Item>
          <Nav.Link 
            active={activeTab === 'payroll'}
            onClick={() => setActiveTab('payroll')}
          >
            💰 Payroll (Ctrl+P)
          </Nav.Link>
        </Nav.Item>
        <Nav.Item>
          <Nav.Link 
            active={activeTab === 'employees'}
            onClick={() => setActiveTab('employees')}
          >
            👥 Employees
          </Nav.Link>
        </Nav.Item>
        <Nav.Item>
          <Nav.Link 
            active={activeTab === 'reports'}
            onClick={() => setActiveTab('reports')}
          >
            📊 Reports (Ctrl+R)
          </Nav.Link>
        </Nav.Item>
      </Nav>

      {/* Content */}
      {activeTab === 'payroll' && renderPayrollTab()}
      {activeTab === 'employees' && renderEmployeesTab()}
      {activeTab === 'reports' && renderReportsTab()}

      {/* Payroll Processing Modal */}
      <Modal show={showPayrollModal} onHide={() => setShowPayrollModal(false)} size="lg">
        <Modal.Header closeButton>
          <Modal.Title>Process Payroll</Modal.Title>
        </Modal.Header>
        <Modal.Body>
          {selectedEmployee && (
            <div>
              <h5>{selectedEmployee.employee_name}</h5>
              <Table bordered size="sm">
                <tbody>
                  <tr>
                    <td><strong>Hours Worked:</strong></td>
                    <td>{formatHoursWorked(selectedEmployee.hours_worked || 0)}</td>
                  </tr>
                  <tr>
                    <td><strong>Hourly Rate:</strong></td>
                    <td>{formatCurrency(selectedEmployee.hourly_rate || 0)}</td>
                  </tr>
                  <tr>
                    <td><strong>Gross Pay:</strong></td>
                    <td>{formatCurrency(selectedEmployee.gross_pay || 0)}</td>
                  </tr>
                  <tr>
                    <td><strong>Deductions:</strong></td>
                    <td>{formatCurrency(selectedEmployee.deductions || 0)}</td>
                  </tr>
                  <tr className="table-success">
                    <td><strong>Net Pay:</strong></td>
                    <td><strong>{formatCurrency(selectedEmployee.net_pay || 0)}</strong></td>
                  </tr>
                </tbody>
              </Table>
            </div>
          )}
        </Modal.Body>
        <Modal.Footer>
          <Button variant="secondary" onClick={() => setShowPayrollModal(false)}>
            Cancel
          </Button>
          <Button variant="success" onClick={() => {
            handleCalculatePayroll(selectedEmployee?.employee_id);
            setShowPayrollModal(false);
          }}>
            Approve & Process
          </Button>
        </Modal.Footer>
      </Modal>
    </Container>
  );
};

export default FinanceConsole;
