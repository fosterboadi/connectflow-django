# KPI & Performance Management - User Guide

## Overview
The KPI (Key Performance Indicator) system allows managers to track team performance and conduct formal reviews.

---

## 🎯 For Managers

### Step 1: Create KPI Metrics
1. Navigate to **Performance** from the sidebar
2. Click **"KPI Metrics"** or go to `/performance/kpi/metrics/`
3. Click **"Create New Metric"**
4. Fill in:
   - **Name**: e.g., "Task Completion Rate"
   - **Description**: How it's measured
   - **Metric Type**: Numeric, Percentage, Rating, Boolean, or Threshold
   - **Weight**: Importance (1.0 = normal, 2.0 = double weight)
   - **Target Role** (optional): Admin, Manager, or Member
   - **Target Team** (optional): Specific team
   - **Thresholds** (optional): Min, Target, Max values

**Example Metrics:**
- Task Completion Rate (Percentage, Weight 2.0, Target: 90%)
- Deadline Adherence (Percentage, Weight 1.5, Target: 85%)
- Customer Satisfaction (Rating 1-5, Weight 1.0, Target: 4.0)

---

### Step 2: Assign KPIs to Team Members
1. From the metrics list, click **"Assign"** next to a metric
2. **OR** go to `/performance/kpi/assign/`
3. Select:
   - **Metric**: Which KPI to assign
   - **User**: Team member
   - **Review Period**: Monthly, Quarterly, or Custom date range

**Note:** You can assign the same metric to multiple users for the same period.

---

### Step 3: Create Performance Review
1. Go to **Performance** → **"Create Review"** or `/performance/reviews/create/`
2. Fill in:
   - **Employee**: Who you're reviewing
   - **Review Period Start**: e.g., 2025-01-01
   - **Review Period End**: e.g., 2025-01-31
   - **Overall Comments** (optional)

3. Click **"Create Review"**

---

### Step 4: Score Individual Metrics
1. After creating a review, you'll see the **Review Detail** page
2. For each assigned KPI metric:
   - **Calculated Score** is auto-generated based on task data
   - You can **override** the score if needed
   - If overriding, you **must provide a reason**

**Auto-Calculated Scores are based on:**
- Task completion rate
- Deadline adherence
- Task reopen count
- Output volume (tasks completed)

---

### Step 5: Finalize the Review
1. Once all scores are set, click **"Finalize Review"**
2. **This action is PERMANENT**:
   - Locks all scores
   - Prevents further edits
   - Calculates final weighted score
   - Notifies the employee

**Final Score Calculation:**
```
Final Score = (Score1 × Weight1 + Score2 × Weight2 + ...) / Total Weight
```

---

### Step 6: View Team Performance
1. Go to **Performance** → **"Team Overview"** or `/performance/team/overview/`
2. See:
   - All finalized reviews
   - Average team scores
   - Top performers
   - Members needing attention

---

## 👤 For Team Members

### View Your KPIs
1. Click **"My Performance"** from the sidebar
2. See your assigned KPIs for current period
3. Track your progress in real-time

### View Your Performance History
1. Go to **"My Performance"** dashboard
2. See all your past reviews:
   - Scores per metric
   - Final scores
   - Manager comments
   - Trends over time

**You cannot:**
- Create or edit KPIs
- Assign KPIs
- Modify review scores
- Delete reviews

---

## 📊 Review Periods

### Monthly
- Format: `2025-01` (YYYY-MM)
- Covers entire calendar month
- Automatically calculated

### Quarterly
- Format: `2025-Q1` (YYYY-Q#)
- Q1: Jan-Mar
- Q2: Apr-Jun
- Q3: Jul-Sep
- Q4: Oct-Dec

### Custom
- Choose any start and end date
- Useful for probation periods, projects, etc.

---

## 🔒 Security & Permissions

### Admins & Managers Can:
- Create/edit KPI metrics
- Assign KPIs to team members
- Create and finalize reviews
- Override calculated scores
- View team performance

### Members Can:
- View their own KPIs
- View their own reviews
- Track their progress
- **Cannot modify anything**

---

## 🎯 Best Practices

### For Managers:
1. **Define Clear Metrics**: Make expectations measurable
2. **Set Realistic Targets**: Challenge but achievable
3. **Provide Context**: Use comments to explain scores
4. **Review Regularly**: Monthly or quarterly
5. **Be Consistent**: Apply same standards to all
6. **Document Overrides**: Always explain why you changed a score

### For Organizations:
1. **Standardize Metrics**: Use same KPIs across similar roles
2. **Weight Appropriately**: Core duties = higher weight
3. **Review Periods**: Align with pay cycles
4. **Track Trends**: Look for patterns over time
5. **Audit Logs**: System tracks all changes

---

## 🚨 Common Issues

### "I can't create a review"
- Ensure you're a Manager or Admin
- Check that KPIs are assigned for the period
- Verify you have permission to review that user

### "Calculated score is 0"
- User may have no tasks in the review period
- Metric may not have auto-calculation logic
- Manually override if needed

### "Can't finalize review"
- All metrics must have a score (calculated or overridden)
- Review must be in DRAFT status
- You must be the reviewer or an Admin

### "500 Error when accessing pages"
- Clear browser cache
- Check if you're logged in
- Contact system admin if persists

---

## 📈 Metrics Explained

### Task Completion Rate
- **Formula**: (Completed Tasks / Total Tasks) × 100
- **Good**: ≥ 90%
- **Average**: 70-89%
- **Needs Improvement**: < 70%

### Deadline Adherence
- **Formula**: (On-time Tasks / Total Tasks) × 100
- **Good**: ≥ 85%
- **Average**: 65-84%
- **Needs Improvement**: < 65%

### Custom Metrics
- Defined by your organization
- May use manual scoring
- Check metric description for criteria

---

## 🔄 Workflow Summary

```
1. Manager creates KPI Metrics
         ↓
2. Manager assigns KPIs to team members
         ↓
3. Team members work on tasks (tracked automatically)
         ↓
4. Manager creates Performance Review
         ↓
5. System auto-calculates scores from task data
         ↓
6. Manager reviews and optionally overrides scores
         ↓
7. Manager finalizes review (LOCKS IT)
         ↓
8. Team member views their review
         ↓
9. Review stored permanently in history
```

---

## 📞 Support

If you encounter issues:
1. Check this guide first
2. Ask your manager or admin
3. Use the **Support Tickets** system in the app
4. Contact the **AI Assistant** for quick help

---

**Last Updated:** January 2025
**Version:** 1.0
