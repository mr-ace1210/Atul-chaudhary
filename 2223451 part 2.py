import pandas as pd
import re

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
        max_streak = (streak_start, streak_start, 1)

        for i in range(1, len(group)):
            curr_date = group.loc[i, 'attendance_date']

            if (curr_date - prev_date).days == 1:
                total_absent_days += 1
            else:
                if total_absent_days > 3:
                    max_streak = (streak_start, prev_date, total_absent_days)
                streak_start = curr_date
                total_absent_days = 1

            prev_date = curr_date

        if total_absent_days > 3:
            max_streak = (streak_start, prev_date, total_absent_days)

        if max_streak[2] > 3:
            result.append([student_id, max_streak[0], max_streak[1], max_streak[2]])

    return pd.DataFrame(result, columns=['student_id', 'absence_start_date', 'absence_end_date', 'total_absent_days'])

def validate_email(email):
    pattern = r'^[a-zA-Z_][a-zA-Z0-9_]*@[a-zA-Z]+\.com$'
    return re.match(pattern, email) is not None

def run():
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

    students_data = {
        'student_id': [101, 102, 103],
        'student_name': ['Alice Johnson', 'Bob Smith', 'Charlie Brown'],
        'parent_email': ['alice_parent@example.com', 'bob_parent@example.com', 'invalid_email.com']
    }
    students_df = pd.DataFrame(students_data)

    merged_df = pd.merge(absence_streaks_df, students_df, on='student_id', how='left')
    merged_df['email'] = merged_df['parent_email'].apply(lambda x: x if validate_email(x) else None)

    def create_message(row):
        if row['email']:
            return f"Dear Parent, your child {row['student_name']} was absent from {row['absence_start_date'].strftime('%d-%m-%Y')} to {row['absence_end_date'].strftime('%d-%m-%Y')} for {row['total_absent_days']} days. Please ensure their attendance improves."
        return None

    merged_df['msg'] = merged_df.apply(create_message, axis=1)
    merged_df['absence_start_date'] = merged_df['absence_start_date'].dt.strftime('%d-%m-%Y')
    merged_df['absence_end_date'] = merged_df['absence_end_date'].dt.strftime('%d-%m-%Y')

    final_df = merged_df[['student_id', 'absence_start_date', 'absence_end_date', 'total_absent_days', 'email', 'msg']]
    return final_df

print(run())
