import pandas as pd

def find_absence_streaks(attendance_df):

    attendance_df['attendance_date'] = pd.to_datetime(attendance_df['attendance_date'])
    
    attendance_df = attendance_df.sort_values(by=['student_id', 'attendance_date'])
    
    result = []
    
    for student_id, group in attendance_df.groupby('student_id'):
        group = group[group['status'] == 'Absent'].reset_index(drop=True)
        
        if group.empty:
            continue
        
        streak_start = group.loc[0, 'attendance_date']
        prev_date = streak_start
        total_absent_days = 1
        latest_streak = (streak_start, streak_start, 1)
        
        for i in range(1, len(group)):
            curr_date = group.loc[i, 'attendance_date']
            
            if (curr_date - prev_date).days == 1:
                total_absent_days += 1
            else:
                if total_absent_days > 3:
                    latest_streak = (streak_start, prev_date, total_absent_days)
                streak_start = curr_date
                total_absent_days = 1
            
            prev_date = curr_date
        
        if total_absent_days > 3:
            latest_streak = (streak_start, prev_date, total_absent_days)
        
        if latest_streak[2] > 3:
            result.append([student_id, latest_streak[0], latest_streak[1], latest_streak[2]])
    
    return pd.DataFrame(result, columns=['student_id', 'absence_start_date', 'absence_end_date', 'total_absent_days'])

# Step 1: Creating attendance data
attendance_data = {
    'student_id': [101, 101, 101, 101, 101, 102, 102, 102, 102, 103, 103, 103, 103, 103],
    'attendance_date': ['2024-03-01', '2024-03-02', '2024-03-03', '2024-03-04', '2024-03-05',
                        '2024-03-02', '2024-03-03', '2024-03-04', '2024-03-05',
                        '2024-03-05', '2024-03-06', '2024-03-07', '2024-03-08', '2024-03-09'],
    'status': ['Absent', 'Absent', 'Absent', 'Absent', 'Present', 
               'Absent', 'Absent', 'Absent', 'Absent', 
               'Absent', 'Absent', 'Absent', 'Absent', 'Absent']
}
attendance_df = pd.DataFrame(attendance_data)

absence_streaks_df = find_absence_streaks(attendance_df)

absence_streaks_df['absence_start_date'] = absence_streaks_df['absence_start_date'].dt.strftime('%Y-%m-%d')
absence_streaks_df['absence_end_date'] = absence_streaks_df['absence_end_date'].dt.strftime('%Y-%m-%d')

print(absence_streaks_df)
