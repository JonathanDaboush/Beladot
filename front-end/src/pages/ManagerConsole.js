import React, { useState, useEffect } from 'react';
import { Container, Row, Col, Card, Table, Button, Badge, Nav, Form, Modal, Alert } from 'react-bootstrap';
import managerService from '../services/managerService';
import { TableSkeleton } from '../components/common/LoadingSkeleton';
import { EmptyEmployeesState } from '../components/common/EmptyState';
import { useKeyboardShortcuts, SHORTCUTS } from '../utils/keyboardShortcuts';
import { formatDate, formatHoursWorked } from '../utils/formatters';
import { useToast } from '../contexts/ToastContext';

/**
 * Manager Console (BambooHR-style)
 * Department-specific employee management with approval workflows
 * Available to: CUSTOMER_SERVICE_MANAGER, FINANCE_MANAGER, TRANSPORT_MANAGER
 * CRITICAL: ZERO cross-department access (managers are department-scoped)
 */
const ManagerConsole = () => {
  const [activeTab, setActiveTab] = useState('approvals');
  const [pendingTimeEntries, setPendingTimeEntries] = useState([]);
  const [pendingLeaveRequests, setPendingLeaveRequests] = useState([]);
  const [employees, setEmployees] = useState([]);
  const [schedule, setSchedule] = useState([]);
  const [selectedItems, setSelectedItems] = useState([]);
  const [showApprovalModal, setShowApprovalModal] = useState(false);
  const [approvalAction, setApprovalAction] = useState('');
  const [approvalReason, setApprovalReason] = useState('');
  const [loading, setLoading] = useState(true);
  const toast = useToast();

  // Keyboard shortcuts
  const shortcuts = [
    { ...SHORTCUTS.MANAGER.APPROVALS, callback: () => setActiveTab('approvals') },
    { ...SHORTCUTS.MANAGER.TEAM, callback: () => setActiveTab('team') },
    { ...SHORTCUTS.MANAGER.APPROVE, callback: () => handleBatchAction('approve') },
    { ...SHORTCUTS.MANAGER.DENY, callback: () => handleBatchAction('deny') },
  ];
  useKeyboardShortcuts(shortcuts, [selectedItems]);

  useEffect(() => {
    loadManagerData();
  }, [activeTab]);

  const loadManagerData = async () => {
    try {
      setLoading(true);
      if (activeTab === 'approvals') {
        const [timeEntries, leaveRequests] = await Promise.all([
          managerService.getPendingTimeEntries(),
          managerService.getPendingLeaveRequests(),
        ]);
        setPendingTimeEntries(timeEntries.items || timeEntries || []);
        setPendingLeaveRequests(leaveRequests.items || leaveRequests || []);
      } else if (activeTab === 'team') {
        const data = await managerService.getDepartmentEmployees();
        setEmployees(data.items || data || []);
      } else if (activeTab === 'schedule') {
        const startDate = new Date();
        const endDate = new Date();
        endDate.setDate(endDate.getDate() + 14);
        const data = await managerService.getDepartmentSchedule(
          startDate.toISOString().split('T')[0],
          endDate.toISOString().split('T')[0]
        );
        setSchedule(data.items || data || []);
      }
    } catch (err) {
      toast.error('Failed to load manager data');
    } finally {
      setLoading(false);
    }
  };

  const handleApproveTimeEntry = async (entryId) => {
    try {
      await managerService.approveTimeEntry(entryId);
      toast.success('Time entry approved');
      loadManagerData();
    } catch (err) {
      toast.error('Failed to approve time entry');
    }
  };

  const handleRejectTimeEntry = async (entryId, reason) => {
    try {
      await managerService.rejectTimeEntry(entryId, reason);
      toast.success('Time entry rejected');
      loadManagerData();
    } catch (err) {
      toast.error('Failed to reject time entry');
    }
  };

  const handleApproveLeave = async (leaveId) => {
    try {
      await managerService.approveLeaveRequest(leaveId);
      toast.success('Leave request approved');
      loadManagerData();
    } catch (err) {
      toast.error('Failed to approve leave');
    }
  };

  const handleDenyLeave = async (leaveId, reason) => {
    try {
      await managerService.denyLeaveRequest(leaveId, reason);
      toast.success('Leave request denied');
      loadManagerData();
    } catch (err) {
      toast.error('Failed to deny leave');
    }
  };

  const handleBatchAction = async (action) => {
    if (selectedItems.length === 0) {
      toast.error('No items selected');
      return;
    }

    setApprovalAction(action);
    setShowApprovalModal(true);
  };

  const handleBatchApproval = async () => {
    if (approvalAction === 'deny' && !approvalReason.trim()) {
      toast.error('Reason is required for denial');
      return;
    }

    try {
      if (approvalAction === 'approve') {
        await managerService.bulkApprove({ ids: selectedItems });
        toast.success(`${selectedItems.length} items approved`);
      } else {
        await managerService.bulkDeny({ ids: selectedItems, reason: approvalReason });
        toast.success(`${selectedItems.length} items denied`);
      }
      setSelectedItems([]);
      setShowApprovalModal(false);
      setApprovalReason('');
      loadManagerData();
    } catch (err) {
      toast.error('Batch action failed');
    }
  };

  const toggleSelection = (id) => {
    setSelectedItems(prev =>
      prev.includes(id) ? prev.filter(i => i !== id) : [...prev, id]
    );
  };

  const renderApprovalsTab = () => (
    <div>
      <div className="d-flex justify-content-between align-items-center mb-3">
        <h4>Approval Queue</h4>
        <div className="d-flex gap-2">
          <Button
            variant="success"
            disabled={selectedItems.length === 0}
            onClick={() => handleBatchAction('approve')}
          >
            ✅ Approve Selected ({selectedItems.length}) [Y]
          </Button>
          <Button
            variant="danger"
            disabled={selectedItems.length === 0}
            onClick={() => handleBatchAction('deny')}
          >
            ❌ Deny Selected ({selectedItems.length}) [N]
          </Button>
        </div>
      </div>

      {/* Time Entry Approvals */}
      <Card className="mb-4">
        <Card.Header className="bg-light">
          <strong>⏰ Pending Time Entries</strong>
        </Card.Header>
        <Card.Body className="p-0">
          {loading ? (
            <TableSkeleton rows={5} />
          ) : pendingTimeEntries.length === 0 ? (
            <div className="text-center py-4">
              <p className="text-muted mb-0">No pending time entries</p>
            </div>
          ) : (
            <Table hover className="mb-0">
              <thead className="table-light">
                <tr>
                  <th style={{ width: '40px' }}>
                    <Form.Check type="checkbox" />
                  </th>
                  <th>Employee</th>
                  <th>Date</th>
                  <th>Clock In</th>
                  <th>Clock Out</th>
                  <th>Hours</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {pendingTimeEntries.map((entry) => (
                  <tr key={entry.id}>
                    <td>
                      <Form.Check
                        type="checkbox"
                        checked={selectedItems.includes(entry.id)}
                        onChange={() => toggleSelection(entry.id)}
                      />
                    </td>
                    <td><strong>{entry.employee_name}</strong></td>
                    <td>{formatDate(entry.date)}</td>
                    <td>{entry.clock_in_time}</td>
                    <td>{entry.clock_out_time}</td>
                    <td><Badge bg="info">{formatHoursWorked(entry.hours_worked)}</Badge></td>
                    <td>
                      <Button
                        variant="link"
                        size="sm"
                        className="p-0 me-2 text-success"
                        onClick={() => handleApproveTimeEntry(entry.id)}
                      >
                        ✅ Approve
                      </Button>
                      <Button
                        variant="link"
                        size="sm"
                        className="p-0 text-danger"
                        onClick={() => handleRejectTimeEntry(entry.id, 'Invalid time entry')}
                      >
                        ❌ Reject
                      </Button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </Table>
          )}
        </Card.Body>
      </Card>

      {/* Leave Request Approvals */}
      <Card>
        <Card.Header className="bg-light">
          <strong>🏖️ Pending Leave Requests</strong>
        </Card.Header>
        <Card.Body className="p-0">
          {loading ? (
            <TableSkeleton rows={5} />
          ) : pendingLeaveRequests.length === 0 ? (
            <div className="text-center py-4">
              <p className="text-muted mb-0">No pending leave requests</p>
            </div>
          ) : (
            <Table hover className="mb-0">
              <thead className="table-light">
                <tr>
                  <th style={{ width: '40px' }}>
                    <Form.Check type="checkbox" />
                  </th>
                  <th>Employee</th>
                  <th>Type</th>
                  <th>Start Date</th>
                  <th>End Date</th>
                  <th>Days</th>
                  <th>Reason</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {pendingLeaveRequests.map((leave) => (
                  <tr key={leave.id}>
                    <td>
                      <Form.Check
                        type="checkbox"
                        checked={selectedItems.includes(leave.id)}
                        onChange={() => toggleSelection(leave.id)}
                      />
                    </td>
                    <td><strong>{leave.employee_name}</strong></td>
                    <td><Badge bg="secondary">{leave.leave_type}</Badge></td>
                    <td>{formatDate(leave.start_date)}</td>
                    <td>{formatDate(leave.end_date)}</td>
                    <td><Badge bg="info">{leave.days_requested}</Badge></td>
                    <td><small className="text-muted">{leave.reason}</small></td>
                    <td>
                      <Button
                        variant="link"
                        size="sm"
                        className="p-0 me-2 text-success"
                        onClick={() => handleApproveLeave(leave.id)}
                      >
                        ✅ Approve
                      </Button>
                      <Button
                        variant="link"
                        size="sm"
                        className="p-0 text-danger"
                        onClick={() => handleDenyLeave(leave.id, 'Insufficient coverage')}
                      >
                        ❌ Deny
                      </Button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </Table>
          )}
        </Card.Body>
      </Card>
    </div>
  );

  const renderTeamTab = () => (
    <div>
      <div className="d-flex justify-content-between align-items-center mb-3">
        <h4>Department Team</h4>
        <Button variant="primary">+ Add Employee</Button>
      </div>

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
                <th>Email</th>
                <th>Position</th>
                <th>Hire Date</th>
                <th>Status</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {employees.map((employee) => (
                <tr key={employee.id}>
                  <td>
                    <strong>{employee.first_name} {employee.last_name}</strong>
                  </td>
                  <td>{employee.email}</td>
                  <td><Badge bg="info">{employee.job_title || 'Employee'}</Badge></td>
                  <td>{formatDate(employee.hire_date)}</td>
                  <td>
                    <Badge bg={employee.is_active ? 'success' : 'secondary'}>
                      {employee.is_active ? 'Active' : 'Inactive'}
                    </Badge>
                  </td>
                  <td>
                    <Button variant="link" size="sm" className="p-0 me-2">
                      ✏️ Edit
                    </Button>
                    <Button variant="link" size="sm" className="p-0">
                      📊 Performance
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

  const renderScheduleTab = () => (
    <div>
      <h4 className="mb-3">Department Schedule (Next 2 Weeks)</h4>

      {loading ? (
        <TableSkeleton rows={10} />
      ) : schedule.length === 0 ? (
        <Card className="text-center py-5">
          <Card.Body>
            <div style={{ fontSize: '4rem' }}>📅</div>
            <h5 className="mt-3">No Schedule Data</h5>
            <p className="text-muted">Schedule information will appear here</p>
          </Card.Body>
        </Card>
      ) : (
        <Card>
          <Table responsive hover className="mb-0">
            <thead className="table-light">
              <tr>
                <th>Date</th>
                <th>Employee</th>
                <th>Shift</th>
                <th>Start Time</th>
                <th>End Time</th>
                <th>Status</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {schedule.map((shift) => (
                <tr key={shift.id}>
                  <td>{formatDate(shift.date)}</td>
                  <td><strong>{shift.employee_name}</strong></td>
                  <td><Badge bg="primary">{shift.shift_type}</Badge></td>
                  <td>{shift.start_time}</td>
                  <td>{shift.end_time}</td>
                  <td>
                    {shift.is_confirmed ? (
                      <Badge bg="success">Confirmed</Badge>
                    ) : (
                      <Badge bg="warning">Pending</Badge>
                    )}
                  </td>
                  <td>
                    <Button variant="link" size="sm" className="p-0">
                      ✏️ Modify
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

  return (
    <Container fluid className="py-4">
      <div className="d-flex justify-content-between align-items-center mb-4">
        <div>
          <h1>👔 Manager Console</h1>
          <p className="text-muted mb-0">BambooHR-style department management</p>
        </div>
        <Alert variant="warning" className="mb-0 py-2">
          <small><strong>Department Scoped:</strong> You only see your department employees</small>
        </Alert>
      </div>

      {/* Navigation Tabs */}
      <Nav variant="tabs" className="mb-4">
        <Nav.Item>
          <Nav.Link 
            active={activeTab === 'approvals'}
            onClick={() => setActiveTab('approvals')}
          >
            ✅ Approvals (Ctrl+A)
          </Nav.Link>
        </Nav.Item>
        <Nav.Item>
          <Nav.Link 
            active={activeTab === 'team'}
            onClick={() => setActiveTab('team')}
          >
            👥 Team (Ctrl+T)
          </Nav.Link>
        </Nav.Item>
        <Nav.Item>
          <Nav.Link 
            active={activeTab === 'schedule'}
            onClick={() => setActiveTab('schedule')}
          >
            📅 Schedule
          </Nav.Link>
        </Nav.Item>
      </Nav>

      {/* Content */}
      {activeTab === 'approvals' && renderApprovalsTab()}
      {activeTab === 'team' && renderTeamTab()}
      {activeTab === 'schedule' && renderScheduleTab()}

      {/* Batch Approval Modal */}
      <Modal show={showApprovalModal} onHide={() => setShowApprovalModal(false)}>
        <Modal.Header closeButton>
          <Modal.Title>
            {approvalAction === 'approve' ? '✅ Batch Approve' : '❌ Batch Deny'}
          </Modal.Title>
        </Modal.Header>
        <Modal.Body>
          <Alert variant={approvalAction === 'approve' ? 'success' : 'warning'}>
            You are about to {approvalAction} <strong>{selectedItems.length}</strong> items.
          </Alert>
          
          {approvalAction === 'deny' && (
            <Form.Group>
              <Form.Label><strong>Reason (Required)*</strong></Form.Label>
              <Form.Control
                as="textarea"
                rows={3}
                placeholder="Provide a reason for denial..."
                value={approvalReason}
                onChange={(e) => setApprovalReason(e.target.value)}
                required
              />
            </Form.Group>
          )}
        </Modal.Body>
        <Modal.Footer>
          <Button variant="secondary" onClick={() => setShowApprovalModal(false)}>
            Cancel
          </Button>
          <Button 
            variant={approvalAction === 'approve' ? 'success' : 'danger'}
            onClick={handleBatchApproval}
            disabled={approvalAction === 'deny' && !approvalReason.trim()}
          >
            Confirm {approvalAction === 'approve' ? 'Approval' : 'Denial'}
          </Button>
        </Modal.Footer>
      </Modal>
    </Container>
  );
};

export default ManagerConsole;
