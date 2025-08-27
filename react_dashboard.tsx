import React, { useState, useEffect } from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, BarChart, Bar, PieChart, Pie, Cell } from 'recharts';

// API service
const API_BASE_URL = '/api';

const api = {
  getDashboardStats: () => fetch(`${API_BASE_URL}/dashboard-stats`).then(r => r.json()),
  getEmployees: () => fetch(`${API_BASE_URL}/employees`).then(r => r.json()),
  getMonthlyCompliance: (year, month) => fetch(`${API_BASE_URL}/monthly-compliance/${year}/${month}`).then(r => r.json()),
  getEmployeeStats: (id, year, month) => fetch(`${API_BASE_URL}/employee-stats/${id}/${year}/${month}`).then(r => r.json()),
  getDataQualityIssues: () => fetch(`${API_BASE_URL}/data-quality-issues`).then(r => r.json()),
  getWeeklyPatterns: (id, year, month) => fetch(`${API_BASE_URL}/weekly-patterns/${id}/${year}/${month}`).then(r => r.json()),
  getEmployeeTrends: (id, months = 6) => fetch(`${API_BASE_URL}/trends/${id}?months_back=${months}`).then(r => r.json()),
  getDepartmentStats: (year, month) => fetch(`${API_BASE_URL}/department-stats/${year}/${month}`).then(r => r.json()),
  exportMonthlyReport: (year, month) => `${API_BASE_URL}/export/monthly-report/${year}/${month}`
};

// Loading component
const LoadingSpinner = () => (
  <div className="flex justify-center items-center p-8">
    <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
  </div>
);

// Alert component for data quality issues
const AlertBanner = ({ issues }) => {
  if (!issues || issues.length === 0) return null;

  return (
    <div className="bg-red-50 border-l-4 border-red-400 p-4 mb-6">
      <div className="flex">
        <div className="flex-shrink-0">
          <svg className="h-5 w-5 text-red-400" viewBox="0 0 20 20" fill="currentColor">
            <path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
          </svg>
        </div>
        <div className="ml-3">
          <p className="text-sm text-red-700">
            <strong>Data Quality Alert:</strong> {issues.length} issue(s) detected with attendance records.
            Check the Data Quality tab for details.
          </p>
        </div>
      </div>
    </div>
  );
};

// Dashboard Overview Component
const Dashboard = () => {
  const [dashboardData, setDashboardData] = useState(null);
  const [dataIssues, setDataIssues] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const loadData = async () => {
      try {
        const [stats, issues] = await Promise.all([
          api.getDashboardStats(),
          api.getDataQualityIssues()
        ]);
        setDashboardData(stats);
        setDataIssues(issues);
      } catch (error) {
        console.error('Error loading dashboard data:', error);
      } finally {
        setLoading(false);
      }
    };

    loadData();
  }, []);

  if (loading) return <LoadingSpinner />;

  const complianceData = dashboardData ? [
    { name: 'Compliant', value: dashboardData.compliant_employees, color: '#10B981' },
    { name: 'Non-Compliant', value: dashboardData.non_compliant_employees, color: '#EF4444' },
    { name: 'Other', value: dashboardData.total_employees - dashboardData.compliant_employees - dashboardData.non_compliant_employees, color: '#F59E0B' }
  ] : [];

  return (
    <div className="p-6">
      <AlertBanner issues={dataIssues} />
      
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center">
            <div className="p-2 bg-blue-100 rounded-md">
              <svg className="w-6 h-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197m13.5-9a2.5 2.5 0 11-5 0 2.5 2.5 0 015 0z" />
              </svg>
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Total Employees</p>
              <p className="text-2xl font-semibold text-gray-900">{dashboardData?.total_employees || 0}</p>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center">
            <div className="p-2 bg-green-100 rounded-md">
              <svg className="w-6 h-6 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Compliance Rate</p>
              <p className="text-2xl font-semibold text-gray-900">{dashboardData?.compliance_rate?.toFixed(1) || 0}%</p>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center">
            <div className="p-2 bg-yellow-100 rounded-md">
              <svg className="w-6 h-6 text-yellow-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Avg Hours/Day</p>
              <p className="text-2xl font-semibold text-gray-900">{dashboardData?.average_hours_per_day?.toFixed(1) || 0}</p>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center">
            <div className="p-2 bg-red-100 rounded-md">
              <svg className="w-6 h-6 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.996-.833-2.732 0L3.732 16c-.77.833.192 2.5 1.732 2.5z" />
              </svg>
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Data Issues</p>
              <p className="text-2xl font-semibold text-gray-900">{dashboardData?.total_data_issues || 0}</p>
            </div>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-medium text-gray-900 mb-4">Compliance Distribution</h3>
          <ResponsiveContainer width="100%" height={300}>
            <PieChart>
              <Pie
                data={complianceData}
                cx="50%"
                cy="50%"
                labelLine={false}
                label={({ name, value }) => `${name}: ${value}`}
                outerRadius={80}
                fill="#8884d8"
                dataKey="value"
              >
                {complianceData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={entry.color} />
                ))}
              </Pie>
              <Tooltip />
            </PieChart>
          </ResponsiveContainer>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-medium text-gray-900 mb-4">Common Data Issues</h3>
          <div className="space-y-3">
            {dashboardData?.most_common_issues?.map((issue, index) => (
              <div key={index} className="flex justify-between items-center p-3 bg-gray-50 rounded">
                <span className="text-sm font-medium text-gray-900">{issue.type.replace('_', ' ').toUpperCase()}</span>
                <span className="text-sm text-gray-600">{issue.count} cases</span>
              </div>
            )) || <p className="text-gray-500">No issues detected</p>}
          </div>
        </div>
      </div>
    </div>
  );
};

// Monthly Report Component
const MonthlyReport = () => {
  const [reportData, setReportData] = useState(null);
  const [selectedMonth, setSelectedMonth] = useState(() => {
    const now = new Date();
    return { year: now.getFullYear(), month: now.getMonth() + 1 };
  });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const loadReport = async () => {
      setLoading(true);
      try {
        const data = await api.getMonthlyCompliance(selectedMonth.year, selectedMonth.month);
        setReportData(data);
      } catch (error) {
        console.error('Error loading monthly report:', error);
      } finally {
        setLoading(false);
      }
    };

    loadReport();
  }, [selectedMonth]);

  const handleMonthChange = (e) => {
    const [year, month] = e.target.value.split('-');
    setSelectedMonth({ year: parseInt(year), month: parseInt(month) });
  };

  const getComplianceColor = (status) => {
    switch (status) {
      case 'compliant': return 'text-green-800 bg-green-100';
      case 'partial': return 'text-yellow-800 bg-yellow-100';
      case 'non_compliant': return 'text-red-800 bg-red-100';
      default: return 'text-gray-800 bg-gray-100';
    }
  };

  const handleExport = () => {
    const url = api.exportMonthlyReport(selectedMonth.year, selectedMonth.month);
    window.open(url, '_blank');
  };

  if (loading) return <LoadingSpinner />;

  return (
    <div className="p-6">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-2xl font-bold text-gray-900">Monthly Compliance Report</h1>
        <div className="flex space-x-4">
          <input
            type="month"
            value={`${selectedMonth.year}-${selectedMonth.month.toString().padStart(2, '0')}`}
            onChange={handleMonthChange}
            className="border border-gray-300 rounded-md px-3 py-2"
          />
          <button
            onClick={handleExport}
            className="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700 transition-colors"
          >
            Export Excel
          </button>
        </div>
      </div>

      {reportData && (
        <div className="bg-white rounded-lg shadow overflow-hidden">
          <div className="px-6 py-4 border-b border-gray-200">
            <h3 className="text-lg font-medium text-gray-900">
              Report for {new Date(selectedMonth.year, selectedMonth.month - 1).toLocaleDateString('en-US', { month: 'long', year: 'numeric' })}
            </h3>
            <p className="text-sm text-gray-600 mt-1">Total Employees: {reportData.total_employees}</p>
          </div>

          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Employee</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Department</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Days</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Hours</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Avg Hours/Day</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Compliance</th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {reportData.employee_stats?.map((empStat, index) => (
                  <tr key={empStat.employee_info?.ID_PERSONA || index} className="hover:bg-gray-50">
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="text-sm font-medium text-gray-900">
                        {empStat.employee_info?.NOMBRE} {empStat.employee_info?.APELLIDO}
                      </div>
                      <div className="text-sm text-gray-500">ID: {empStat.employee_info?.ID_PERSONA}</div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      {empStat.employee_info?.DEPARTAMENTO || 'N/A'}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      {empStat.stats?.total_days_attended || 0}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      {empStat.stats?.total_hours_worked?.toFixed(1) || 0}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      {empStat.stats?.average_hours_per_day?.toFixed(1) || 0}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${getComplianceColor(empStat.stats?.overall_compliance)}`}>
                        {empStat.stats?.overall_compliance?.replace('_', ' ').toUpperCase() || 'UNKNOWN'}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
};

// Employee Details Component
const EmployeeDetails = () => {
  const [employees, setEmployees] = useState([]);
  const [selectedEmployee, setSelectedEmployee] = useState(null);
  const [employeeStats, setEmployeeStats] = useState(null);
  const [weeklyPatterns, setWeeklyPatterns] = useState(null);
  const [selectedMonth, setSelectedMonth] = useState(() => {
    const now = new Date();
    return { year: now.getFullYear(), month: now.getMonth() + 1 };
  });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const loadEmployees = async () => {
      try {
        const data = await api.getEmployees();
        setEmployees(data);
        if (data.length > 0) {
          setSelectedEmployee(data[0].ID_PERSONA);
        }
      } catch (error) {
        console.error('Error loading employees:', error);
      } finally {
        setLoading(false);
      }
    };

    loadEmployees();
  }, []);

  useEffect(() => {
    if (selectedEmployee) {
      const loadEmployeeData = async () => {
        try {
          const [stats, patterns] = await Promise.all([
            api.getEmployeeStats(selectedEmployee, selectedMonth.year, selectedMonth.month),
            api.getWeeklyPatterns(selectedEmployee, selectedMonth.year, selectedMonth.month)
          ]);
          setEmployeeStats(stats);
          setWeeklyPatterns(patterns);
        } catch (error) {
          console.error('Error loading employee data:', error);
        }
      };

      loadEmployeeData();
    }
  }, [selectedEmployee, selectedMonth]);

  const handleMonthChange = (e) => {
    const [year, month] = e.target.value.split('-');
    setSelectedMonth({ year: parseInt(year), month: parseInt(month) });
  };

  if (loading) return <LoadingSpinner />;

  return (
    <div className="p-6">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-2xl font-bold text-gray-900">Employee Details</h1>
        <div className="flex space-x-4">
          <select
            value={selectedEmployee || ''}
            onChange={(e) => setSelectedEmployee(parseInt(e.target.value))}
            className="border border-gray-300 rounded-md px-3 py-2"
          >
            {employees.map(emp => (
              <option key={emp.ID_PERSONA} value={emp.ID_PERSONA}>
                {emp.NOMBRE} {emp.APELLIDO}
              </option>
            ))}
          </select>
          <input
            type="month"
            value={`${selectedMonth.year}-${selectedMonth.month.toString().padStart(2, '0')}`}
            onChange={handleMonthChange}
            className="border border-gray-300 rounded-md px-3 py-2"
          />
        </div>
      </div>

      {employeeStats && (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-6">
          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-lg font-medium text-gray-900 mb-2">Days Attended</h3>
            <p className="text-3xl font-bold text-blue-600">{employeeStats.total_days_attended}</p>
            <p className="text-sm text-gray-500 mt-1">
              Status: <span className={`font-medium ${employeeStats.days_compliance === 'compliant' ? 'text-green-600' : 'text-red-600'}`}>
                {employeeStats.days_compliance?.replace('_', ' ').toUpperCase()}
              </span>
            </p>
          </div>

          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-lg font-medium text-gray-900 mb-2">Total Hours</h3>
            <p className="text-3xl font-bold text-green-600">{employeeStats.total_hours_worked?.toFixed(1)}</p>
            <p className="text-sm text-gray-500 mt-1">
              Avg: {employeeStats.average_hours_per_day?.toFixed(1)} hrs/day
            </p>
          </div>

          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-lg font-medium text-gray-900 mb-2">Overall Compliance</h3>
            <p className={`text-3xl font-bold ${
              employeeStats.overall_compliance === 'compliant' ? 'text-green-600' :
              employeeStats.overall_compliance === 'partial' ? 'text-yellow-600' : 'text-red-600'
            }`}>
              {employeeStats.overall_compliance?.replace('_', ' ').toUpperCase()}
            </p>
            <p className="text-sm text-gray-500 mt-1">
              Hours: {employeeStats.hours_compliance?.replace('_', ' ')} | Pattern: {employeeStats.pattern_compliance ? 'Valid' : 'Invalid'}
            </p>
          </div>
        </div>
      )}

      {weeklyPatterns && (
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-medium text-gray-900 mb-4">Weekly Patterns</h3>
          <div className="space-y-4">
            {weeklyPatterns.weekly_patterns?.map((week, index) => (
              <div key={index} className="border border-gray-200 rounded-lg p-4">
                <div className="flex justify-between items-center mb-2">
                  <h4 className="font-medium text-gray-900">Week {week.week_number}</h4>
                  <div className="flex space-x-4 text-sm text-gray-600">
                    <span>Days: {week.days_attended}</span>
                    <span>Hours: {week.total_hours}h</span>
                    <span className={`px-2 py-1 rounded ${week.meets_requirement ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'}`}>
                      {week.meets_requirement ? 'Valid' : 'Invalid'}
                    </span>
                  </div>
                </div>
                <div className="grid grid-cols-7 gap-2 mt-3">
                  {week.daily_details?.map((day, dayIndex) => (
                    <div key={dayIndex} className={`text-xs p-2 rounded text-center ${
                      day.is_complete ? 'bg-green-50 border border-green-200' : 'bg-gray-50 border border-gray-200'
                    }`}>
                      <div className="font-medium">{new Date(day.date).toLocaleDateString('en-US', { weekday: 'short' })}</div>
                      <div>{new Date(day.date).getDate()}</div>
                      {day.entry_time && <div className="text-blue-600">{day.entry_time}</div>}
                      {day.exit_time && <div className="text-red-600">{day.exit_time}</div>}
                      {day.hours_worked && <div className="font-medium">{day.hours_worked}h</div>}
                    </div>
                  ))}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

// Data Quality Component
const DataQuality = () => {
  const [issues, setIssues] = useState([]);
  const [loading, setLoading] = useState(true);
  const [dateRange, setDateRange] = useState({
    start: new Date(Date.now() - 30 * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
    end: new Date().toISOString().split('T')[0]
  });

  useEffect(() => {
    const loadIssues = async () => {
      setLoading(true);
      try {
        const data = await api.getDataQualityIssues();
        setIssues(data);
      } catch (error) {
        console.error('Error loading data quality issues:', error);
      } finally {
        setLoading(false);
      }
    };

    loadIssues();
  }, [dateRange]);

  const getIssueIcon = (type) => {
    switch (type) {
      case 'missing_exit':
        return <svg className="w-5 h-5 text-red-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.996-.833-2.732 0L3.732 16c-.77.833.192 2.5 1.732 2.5z" />
        </svg>;
      case 'missing_entry':
        return <svg className="w-5 h-5 text-yellow-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.996-.833-2.732 0L3.732 16c-.77.833.192 2.5 1.732 2.5z" />
        </svg>;
      default:
        return <svg className="w-5 h-5 text-orange-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.996-.833-2.732 0L3.732 16c-.77.833.192 2.5 1.732 2.5z" />
        </svg>;
    }
  };

  if (loading) return <LoadingSpinner />;

  return (
    <div className="p-6">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-2xl font-bold text-gray-900">Data Quality Issues</h1>
        <div className="text-sm text-gray-600">
          Total Issues: {issues.length}
        </div>
      </div>

      {issues.length === 0 ? (
        <div className="bg-green-50 border border-green-200 rounded-lg p-8 text-center">
          <svg className="mx-auto h-12 w-12 text-green-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          <h3 className="mt-4 text-lg font-medium text-green-900">No Data Quality Issues</h3>
          <p className="mt-2 text-green-700">All attendance records are complete and valid.</p>
        </div>
      ) : (
        <div className="bg-white rounded-lg shadow overflow-hidden">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Issue</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Employee</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Date</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Description</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Records</th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {issues.map((issue, index) => (
                <tr key={index} className="hover:bg-gray-50">
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="flex items-center">
                      {getIssueIcon(issue.issue_type)}
                      <span className="ml-2 text-sm font-medium text-gray-900">
                        {issue.issue_type.replace('_', ' ').toUpperCase()}
                      </span>
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="text-sm font-medium text-gray-900">{issue.employee_name}</div>
                    <div className="text-sm text-gray-500">ID: {issue.employee_id}</div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    {new Date(issue.date).toLocaleDateString()}
                  </td>
                  <td className="px-6 py-4">
                    <div className="text-sm text-gray-900">{issue.description}</div>
                    {issue.first_record && (
                      <div className="text-xs text-gray-500 mt-1">
                        First: {new Date(issue.first_record).toLocaleString()}
                      </div>
                    )}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    {issue.total_records}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
};

// Main App Component with Tab Navigation
const App = () => {
  const [activeTab, setActiveTab] = useState('dashboard');

  const tabs = [
    { id: 'dashboard', label: 'Dashboard', icon: '📊' },
    { id: 'monthly-report', label: 'Monthly Report', icon: '📋' },
    { id: 'employee-details', label: 'Employee Details', icon: '👥' },
    { id: 'data-quality', label: 'Data Quality', icon: '🔍' }
  ];

  const renderContent = () => {
    switch (activeTab) {
      case 'dashboard':
        return <Dashboard />;
      case 'monthly-report':
        return <MonthlyReport />;
      case 'employee-details':
        return <EmployeeDetails />;
      case 'data-quality':
        return <DataQuality />;
      default:
        return <Dashboard />;
    }
  };

  return (
    <div className="min-h-screen bg-gray-100">
      <nav className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <h1 className="text-xl font-bold text-gray-900">Attendance Dashboard</h1>
              </div>
              <div className="hidden md:block ml-10">
                <div className="flex items-baseline space-x-4">
                  {tabs.map((tab) => (
                    <button
                      key={tab.id}
                      onClick={() => setActiveTab(tab.id)}
                      className={`px-3 py-2 rounded-md text-sm font-medium transition-colors flex items-center space-x-1 ${
                        activeTab === tab.id
                          ? 'bg-blue-100 text-blue-700'
                          : 'text-gray-600 hover:text-gray-900 hover:bg-gray-100'
                      }`}
                    >
                      <span>{tab.icon}</span>
                      <span>{tab.label}</span>
                    </button>
                  ))}
                </div>
              </div>
            </div>
            <div className="text-sm text-gray-500">
              Last updated: {new Date().toLocaleString()}
            </div>
          </div>
        </div>
      </nav>

      {/* Mobile tab navigation */}
      <div className="md:hidden bg-white border-b">
        <div className="flex overflow-x-auto">
          {tabs.map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`flex-shrink-0 px-4 py-3 text-sm font-medium border-b-2 transition-colors ${
                activeTab === tab.id
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              <span className="mr-1">{tab.icon}</span>
              {tab.label}
            </button>
          ))}
        </div>
      </div>

      <main>
        {renderContent()}
      </main>
    </div>
  );
};

export default App;