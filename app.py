from flask import Flask,flash,redirect,render_template,url_for,request,jsonify,session,abort
from flask_session import Session
import mysql.connector
from datetime import date
from datetime import datetime
from sdmail import sendmail
from tokenreset import token
from itsdangerous import URLSafeTimedSerializer
from key import *
from stoken1 import token1
app=Flask(__name__)
app.secret_key='hello'
app.config['SESSION_TYPE'] = 'filesystem'
mydb=mysql.connector.connect(host="localhost",user="root",password="keerthi",db='last')
Session(app)
@app.route('/')
def main():
    return render_template('main.html')
#============================================index page
@app.route('/index',methods=['GET','POST'])
def index():
    if session.get('user'):
        return redirect({{url_for('index')}}) 
    return render_template('index.html')
#=========================================Faculty login and register
@app.route('/flogin',methods=['GET','POST'])
def flogin():
    if session.get('faculty_id'):
        return redirect(url_for('faculty_dashboard'))
    if request.method=='POST':
        username=request.form['id1']
        password=request.form['password']
        cursor=mydb.cursor(buffered=True)
        cursor.execute('SELECT count(*) from faculty where faculty_id=%s and password=%s',[username,password])
        count=cursor.fetchone()[0]
        print(count)
        if count==1:
            session['faculty_id']=username
            return redirect(url_for("faculty_dashboard"))
        else:
            flash('Invalid Faculty_Id or Password')
            return render_template('faculty_login.html')
    return render_template('faculty_login.html')

@app.route('/fregistration',methods=['GET','POST'])
def fregistration():
    if request.method=='POST':
        id1=request.form['id']
        username = request.form['username']
        password=request.form['password']
        email=request.form['email']
        phnumber=request.form['phone_number']
        
        address=request.form['address']
        role=request.form['role']
        ccode=request.form['ccode']
        Dob=request.form['date_of_birth']
        sex=request.form['gender']
        dept=request.form['department']
        Doj=request.form['joining_date']
        bloodgrp=request.form['blood_group']
        supervisor=request.form['supervisor']
       
        print(Dob,sex,dept,Doj,bloodgrp)
        code="codegnan@9"
        if code == ccode:
            cursor=mydb.cursor(buffered=True)
            cursor.execute('select count(*) from faculty where faculty_id=%s',[id1])
            count=cursor.fetchone()[0]
            cursor.execute('select count(*) from faculty where email=%s',[email])
            count1=cursor.fetchone()[0]
            cursor.close()
            if count==1:
                flash('username already in use')
                return render_template('faculty_login.html')
            elif count1==1:
                flash('Email already in use')
                return render_template('faculty_login.html')
            
            data={'faculty_id':id1,'username':username,'password':password,'email':email,'phone_number':phnumber,'address':address,'role':role,'Dob':Dob,'sex':sex,'dept':dept,'Doj':Doj,'bg':bloodgrp,'supervisor':supervisor}
            subject='Email Confirmation'
            body=f"Thanks for signing up\n\nfollow this link for further steps-{url_for('fconfirm',token=token(data,salt),_external=True)}"
            sendmail(to=email,subject=subject,body=body)
            flash('Confirmation link sent to mail')
            return redirect(url_for('fregistration'))
        else:
            flash("faculty code is wrong unauthorized access!")
            return redirect(url_for('fregistration'))
    return render_template('faculty_registration.html')
@app.route('/fconfirm/<token>')
def fconfirm(token):
    try:
        serializer=URLSafeTimedSerializer(secret_key)
        data=serializer.loads(token,salt=salt,max_age=180)
    except Exception as e:
      
        return 'Link Expired register again'
    else:
        cursor=mydb.cursor(buffered=True)
        id1=data['faculty_id']
        cursor.execute('select count(*) from faculty where faculty_id=%s',[id1])
        count=cursor.fetchone()[0]
        if count==1:
            cursor.close()
            flash('You are already registerterd!')
            return redirect(url_for('flogin'))
        else:
           
            cursor.execute('INSERT INTO faculty (faculty_id,username, password, email, phone_number, address,role,date_of_birth,gender,department,joining_date,blood_group,supervisor) VALUES (%s,%s,%s, %s, %s, %s, %s,%s,%s,%s,%s,%s,%s)',[data['faculty_id'],data['username'], data['password'], data['email'], data['phone_number'], data['address'],data['role'],data['Dob'],data['sex'],data['dept'],data['Doj'],data['bg'],data['supervisor']])
            mydb.commit()
            cursor.close()
            flash('Details registered!')
            return redirect(url_for('flogin'))
@app.route('/forget',methods=['GET','POST'])
def forgot():
    if request.method=='POST':
        id1=request.form['id1']
        cursor=mydb.cursor(buffered=True)
        cursor.execute('select count(*) from faculty where username=%s',[id1])
        count=cursor.fetchone()[0]
        cursor.close()
        if count==1:
            cursor=mydb.cursor(buffered=True)

            cursor.execute('SELECT email  from faculty where username=%s',[id1])
            email=cursor.fetchone()[0]
            cursor.close()
            subject='Forget Password'
            confirm_link=url_for('reset',token=token(id1,salt=salt2),_external=True)
            body=f"Use this link to reset your password-\n\n{confirm_link}"
            sendmail(to=email,body=body,subject=subject)
            flash('Reset link sent check your email')
            return redirect(url_for('flogin'))
        else:
            flash('Invalid email id')
            return render_template('forgot.html')
    return render_template('forgot.html')


@app.route('/reset/<token>',methods=['GET','POST'])
def reset(token):
    try:
        serializer=URLSafeTimedSerializer(secret_key)
        id1=serializer.loads(token,salt=salt2,max_age=180)
    except:
        abort(404,'Link Expired')
    else:
        if request.method=='POST':
            newpassword=request.form['npassword']
            confirmpassword=request.form['cpassword']
            if newpassword==confirmpassword:
                cursor=mydb.cursor(buffered=True)
                cursor.execute('update  faculty set password=%s where username=%s',[newpassword,id1])
                mydb.commit()
                flash('Reset Successful')
                return redirect(url_for('flogin'))
            else:
                flash('Passwords mismatched')
                return render_template('newpassword.html')
        return render_template('newpassword.html')

@app.route('/faculty_dashboard')
def faculty_dashboard():
    if session.get('faculty_id'):
        cursor=mydb.cursor(buffered=True)
        cursor.execute('select faculty_id from faculty where faculty_id=%s',[session.get('faculty_id')])
        count=cursor.fetchone()[0]
        return render_template('faculty_dashboard.html',count=count)
    else:
        return redirect(url_for('flogin'))
@app.route('/flogout')
def flogout():
    if session.get('faculty_id'):
        session.pop('faculty_id')
        flash('Successfully loged out')
        return redirect(url_for('flogin'))
    else:
        return redirect(url_for('flogin'))
    
#============apply for leave
from datetime import datetime

# Modify the '/apply_leave' route
@app.route('/apply_leave', methods=['GET', 'POST'])
def apply_leave():
    if session.get('faculty_id'):
        if request.method == 'POST':
            faculty_id = session.get('faculty_id')  # Get faculty_id from session
            leave_type = request.form['leave_type']
            start_date = request.form['start_date']
            end_date = request.form['end_date']
            # Calculate the total number of days for leave
            start_date = datetime.strptime(start_date, '%Y-%m-%d')
            end_date = datetime.strptime(end_date, '%Y-%m-%d')
            total_days = (end_date - start_date).days + 1
            
            # Retrieve the monthly leave allocation for the faculty member
            month_year = datetime.now().strftime('%Y-%m')
            print(month_year,faculty_id)
            cursor = mydb.cursor(buffered=True)
            cursor.execute("SELECT total_leavecount FROM MonthlyLeaveAllocations WHERE faculty_id = %s AND month_year = %s", (faculty_id, month_year))
            row = cursor.fetchone()
            print(row)
            if row:
                total_leavecount = row[0]
                # Check if the faculty member has enough leave balance
                if total_days <= total_leavecount:
                    # Insert leave application into the database
                    cursor.execute("INSERT INTO LeaveApplications (faculty_id, leave_type, start_date, end_date) VALUES (%s, %s, %s, %s)", (faculty_id, leave_type, start_date, end_date))
                    mydb.commit()
                    cursor.execute('SELECT  leave_id FROM leaveapplications WHERE faculty_id=%s and start_date=%s and end_date=%s', (session.get('faculty_id'),start_date,end_date))
                    leave_id = cursor.fetchone()[0]
                    cursor.execute('SELECT  department FROM faculty WHERE faculty_id=%s', (session.get('faculty_id'),))
                    dept=cursor.fetchone()[0]
                    cursor.execute('insert into workload (faculty_id,dept,leave_id) values (%s,%s,%s)',(session.get('faculty_id'),dept,leave_id))
                    mydb.commit()
                    
                    cursor.close()
                    
                    flash("Leave application successfully submitted")
                    return redirect(url_for('faculty_dashboard'))  # Redirect to the faculty dashboard after submitting the leave application
                else:
                    flash("Insufficient leave balance")
            else:
                flash("Monthly leave allocation not found for the faculty")
            cursor.close()

        return render_template('leave_application.html')
    else:
        return redirect(url_for('flogin'))


#==================view the leave status
@app.route('/view_status', methods=['GET', 'POST'])
def view_status():
    if session.get('faculty_id'):
        cursor = mydb.cursor(buffered=True)
        cursor.execute('SELECT * FROM leaveapplications WHERE faculty_id=%s', (session.get('faculty_id'),))
        view = cursor.fetchall()

        if request.method == 'POST':
            leave_id = request.form['leave_id']
            cursor.execute('DELETE FROM leaveapplications WHERE leave_id=%s', [leave_id])
            mydb.commit()
            cursor.close()
            flash('Leave application deleted successfully')
            return redirect(url_for('view_status'))

        return render_template('leave_status.html', view=view)
    else:
        return redirect(url_for('flogin'))

#========================= workload assignment
from flask import render_template

@app.route('/workload', methods=['GET', 'POST'])
def workload():
    if session.get('faculty_id'):
        cursor = mydb.cursor(buffered=True)
        cursor.execute('''
            SELECT w.workload_id, w.workload_description, l.leave_id, l.start_date, l.end_date 
            FROM workload AS w 
            JOIN leaveapplications AS l ON w.leave_id = l.leave_id 
            WHERE w.faculty_id = %s
        ''', (session.get('faculty_id'),))
        workload_leaves = cursor.fetchall()

        if request.method == 'POST':
            if 'update' in request.form:
                workload_id = request.form['update']
                new_description = request.form['new_description']
                cursor.execute('''
                    UPDATE workload 
                    SET workload_description = %s 
                    WHERE workload_id = %s
                ''', (new_description, workload_id))
                mydb.commit()
                cursor.close()
                flash('Workload updated')
                return redirect(url_for('workload'))

        return render_template('work_load.html', workload_leaves=workload_leaves)
    else:
        return redirect(url_for('flogin'))



#=============================================================================
#==================== Administrator login
@app.route('/administrator_login',methods=['GET','POST'])
def alogin():
  
    if request.method=='POST':
        email=request.form['email']
        code = request.form['code']
        email1="admin@codegnan.com"
        code1="admin@123"
        if email == email1: 
            if code == code1:
                session['admin']=code1
                return redirect('admindashboard')
        else:
            flash("unauthorized access")
            return redirect(url_for('alogin'))
    
    return render_template('administrator_login.html')
#=======================admin dashboard
@app.route('/admindashboard')
def admindashboard():
    if session.get('admin'):
        return render_template('admin_dashboard.html')
    else:
        return redirect(url_for('alogin'))

#==view all faculty memebers
@app.route('/viewfaculty', methods=['GET', 'POST'])
def viewfaculty():
    if session.get('admin'):
        cursor = mydb.cursor(buffered=True)
        cursor.execute('SELECT * FROM faculty')
        view = cursor.fetchall()
        
        if request.method == 'POST':
            faculty_id = request.form['faculty_id']
            status = request.form['status']
            
            # Validate the status to prevent SQL injection
            if status in ['working', 'not working']:
                cursor.execute('UPDATE faculty SET member_status=%s WHERE faculty_id=%s', [status, faculty_id])
                mydb.commit()
                cursor.close()
                flash(f'Faculty member {faculty_id} updated successfully')
                return redirect(url_for('viewfaculty'))
            else:
                flash('Invalid status')
                
        return render_template('view_faculty.html', view=view)
    else:
        return redirect(url_for('alogin'))


@app.route('/algout')
def alogout():
    if session.get('admin'):
        session.pop('admin')
        flash('successfully log out')
        return redirect(url_for('index'))
    else:
        return redirect(url_for('alogin'))

#=== allocate leaves
@app.route('/view_allocate_leaves', methods=['GET', 'POST'])
def view_allocate_leaves():
    if session.get('admin'):
        cursor = mydb.cursor(buffered=True)
        cursor.execute('''
            SELECT 
                f.faculty_id,
                f.username,
                f.role,
                f.member_status,
                l.leave_type,
                l.start_date,
                l.end_date,
                l.status,
                l.leave_id,
                l.allocated_leaves
            FROM 
                faculty AS f 
            LEFT JOIN 
                leaveapplications AS l 
            ON 
                f.faculty_id = l.faculty_id;
        ''')
        view = cursor.fetchall()
        cursor.close()

        return render_template('all.html', view=view)
    else:
        return redirect(url_for('login'))
@app.route('/update_leave_status', methods=['POST'])
def update_leave_status():
    if session.get('admin'):
        if request.method == 'POST':
            leave_id = request.form.get('leave_id')
            status = request.form.get('status')

            # Update leave status in the database
            cursor = mydb.cursor(buffered=True)
            cursor.execute('UPDATE leaveapplications SET status = %s WHERE leave_id = %s', (status, leave_id))
            mydb.commit()
            cursor.close()
            flash(f'Leave status updated successfully for leave ID {leave_id}')
            return redirect(url_for('view_allocate_leaves'))

        flash('Unauthorized access')
        return redirect(url_for('index'))

@app.route('/fallocate_leaves', methods=['POST'])
def fallocate_leaves():
    if session.get('admin'):
        if request.method == 'POST':
            leave_id = request.form.get('leave_id')
            allocated_leaves = request.form.get('allocated_leaves')


            month_year = datetime.now().strftime('%Y-%m')
            
            

            # Validate and update allocated leaves in the database
            try:

                if int(allocated_leaves) < 0:
                    flash('Allocated leaves cannot be negative')
                    return redirect(url_for('view_allocate_leaves'))
                cursor = mydb.cursor(buffered=True)
                cursor.execute('''
                    SELECT  faculty_id
                    FROM leaveapplications 
                    WHERE leave_id = %s;
                ''', (leave_id,))
                count=cursor.fetchone()[0]
                cursor.execute("SELECT total_leavecount FROM MonthlyLeaveAllocations WHERE faculty_id = %s AND month_year = %s", (count, month_year))
                row = cursor.fetchone()
                allocated_leaves = int(allocated_leaves)

                cursor = mydb.cursor(buffered=True)
                cursor.execute('''
                    SELECT start_date, end_date 
                    FROM leaveapplications 
                    WHERE leave_id = %s;
                ''', (leave_id,))
                start_date, end_date = cursor.fetchone()
                leave_duration = (end_date - start_date).days + 1

                if allocated_leaves > leave_duration:
                    flash(f'Allocated leaves cannot exceed the leave duration of {leave_duration} days')
                    return redirect(url_for('view_allocate_leaves'))

                if row:
                    total_leavecount = row[0]
                # Check if the faculty member has enough leave balance
                    if allocated_leaves <= total_leavecount:
                    # Deduct leave count from the monthly allocation
                        remaining_leavecount = total_leavecount - allocated_leaves
                        cursor.execute("UPDATE MonthlyLeaveAllocations SET total_leavecount = %s WHERE faculty_id = %s AND month_year = %s", (remaining_leavecount, count, month_year))
                        mydb.commit()
 
                

                cursor.execute('''
                    UPDATE leaveapplications 
                    SET allocated_leaves = %s 
                    WHERE leave_id = %s;
                ''', (allocated_leaves, leave_id))
                mydb.commit()
                
                cursor.execute('''
                    SELECT  faculty_id
                    FROM leaveapplications 
                    WHERE leave_id = %s;
                ''', (leave_id,))
                count=cursor.fetchone()[0]
                cursor.close()
                update_leave_usage(count)
                flash(f'Allocated leaves updated successfully for leave ID {leave_id}')
                return redirect(url_for('view_allocate_leaves'))

            except ValueError:
                flash('Invalid input for allocated leaves')
                return redirect(url_for('view_allocate_leaves'))
            
        flash('Unauthorized access')
        return redirect(url_for('index'))


@app.route('/allocate_leave', methods=['POST'])
def allocate_leave():
    if session.get('admin'):
        if request.method == 'POST':
            try:
                # Get form data
                faculty_id = request.form['faculty_id']
                month_year = request.form['month_year']
                total_leavecount = int(request.form['total_leavecount'])

                # Validate inputs
                if total_leavecount < 0:
                    flash('Total leave count cannot be negative', 'error')
                    return redirect(url_for('admindashboard'))

                # Insert or update monthly leave allocation
                cursor = mydb.cursor(buffered=True)
                cursor.execute('INSERT INTO MonthlyLeaveAllocations (faculty_id, month_year,assigned_leavecount, total_leavecount) VALUES (%s, %s, %s,%s) ON DUPLICATE KEY UPDATE total_leavecount = VALUES(total_leavecount)', (faculty_id, month_year, total_leavecount,total_leavecount))
                mydb.commit()
                cursor.close()

                flash('Monthly leave allocated successfully', 'success')
                return redirect(url_for('admindashboard'))

            except ValueError:
                flash('Invalid input for total leave count', 'error')
                return redirect(url_for('admindashboard'))

            except mysql.connector.Error as err:
                flash(f'Error: {err}', 'error')
                return redirect(url_for('admindashboard'))

        return render_template('admin_dashboard.html')
    else:
        return redirect(url_for('admin_login'))

def update_leave_usage(faculty_id):
    cursor = mydb.cursor(buffered=True)
    month_year = datetime.now().strftime('%Y-%m')

    cursor.execute('SELECT total_leavecount FROM MonthlyLeaveAllocations WHERE faculty_id = %s AND month_year = %s', (faculty_id, month_year))
    row = cursor.fetchone()

    if row:
        total_leavecount = row[0]

        cursor.execute('SELECT SUM(allocated_leaves) FROM LeaveApplications WHERE faculty_id = %s', (faculty_id,))
        total_taken_leaves = cursor.fetchone()[0]

        cursor.execute('UPDATE LeaveApplications SET taken_leaves = %s WHERE faculty_id = %s AND MONTH(start_date) = MONTH(NOW()) AND YEAR(start_date) = YEAR(NOW())', (total_taken_leaves, faculty_id))
        mydb.commit()

    cursor.close()



@app.route('/view_workload', methods=['GET', 'POST'])
def view_workload():
    if session.get('admin'):
        cursor = mydb.cursor(buffered=True)

        # Fetch faculty details and workloads
        cursor.execute('''
            SELECT f.faculty_id, f.username, f.role, f.member_status,
                   w.workload_description, w.submission_date, w.status,
                   w.workload_id, w.leave_id, f.department
            FROM faculty AS f
            LEFT JOIN workload AS w ON f.faculty_id = w.faculty_id
        ''')
        workload_data = cursor.fetchall()

        # Fetch leave application details
        cursor.execute('''
            SELECT f.faculty_id, f.username, f.department,
                   l.start_date, l.end_date, l.leave_id
            FROM faculty AS f
            JOIN leaveapplications AS l ON f.faculty_id = l.faculty_id
        ''')
        data = cursor.fetchall()

        # Convert date strings to datetime objects
        
        # Function to check if two date ranges overlap
        def is_conflicting(start1, end1, start2, end2):
            return not (end1 < start2 or start1 > end2)

        # Identify non-conflicting pairs
        ids_without_conflict = set()

        for i in range(len(data)):
            id_i, dept_i, start_i, end_i = data[i][0], data[i][2], data[i][3], data[i][4]
            for j in range(len(data)):
                if i != j and data[i][0] != data[j][0]:
                    id_j, dept_j, start_j, end_j, leave_id_j,leave_id_i = data[j][0], data[j][2], data[j][3], data[j][4], data[j][5],data[i][5]
                    if dept_i == dept_j and not is_conflicting(start_i, end_i, start_j, end_j):
                        ids_without_conflict.add((id_i, id_j, leave_id_j,leave_id_i))
        print(ids_without_conflict)
        if request.method == 'POST':
            if 'reassign_work_id' in request.form:
                work_id = request.form['reassign_work_id']
                new_faculty_id = request.form['new_faculty_id']
                cursor.execute('''
                    UPDATE workload
                    SET faculty_id = %s
                    WHERE workload_id = %s
                ''', [new_faculty_id, work_id])
                mydb.commit()
                flash("Workload reassigned successfully")
                return redirect(url_for('view_workload'))

        cursor.close()

        return render_template('view_workload.html', combined_data=workload_data, data=data, non_conflicting_pairs=ids_without_conflict)
    else:
        return redirect(url_for('alogin'))


@app.route('/assignwork_load/<fid>', methods=['GET', 'POST'])
def assignworkload(fid):
    if session.get('admin'):
        if request.method == 'POST':
            work_id = request.form['work_id']
            assigned_to = request.form['assign']
            cursor = mydb.cursor(buffered=True)

            # Get workload description
            cursor.execute('SELECT workload_description FROM workload WHERE workload_id = %s', [work_id])
            work = cursor.fetchone()[0]

            # Get leave dates for the faculty member to whom workload is assigned
            cursor.execute('''
                SELECT start_date, DATE_ADD(start_date, INTERVAL allocated_leaves DAY) AS end_date 
                FROM leaveapplications 
                WHERE faculty_id = %s
            ''', [assigned_to])
            duration = cursor.fetchone()

            # Get email of the faculty member to whom workload is assigned
            cursor.execute('SELECT email FROM faculty WHERE faculty_id = %s', [assigned_to])
            email = cursor.fetchone()[0]

            # Insert workload assignment
            cursor.execute('INSERT INTO workload_assignment (from_faculty_id, to_faculty_id, workload_id) VALUES (%s, %s, %s)', [fid, assigned_to, work_id])
            mydb.commit()
            cursor.close()
            
            flash(f"Workload assigned to {assigned_to} successfully")
            subject = 'Workload Assignment'
            body = f"Faculty {fid} workload '{work}' has been assigned to you from {duration[0]} to {duration[1]}"
            sendmail(to=email, subject=subject, body=body)
            flash('Workload sent to faculty email')
            return redirect(url_for('view_workload'))

        return redirect(url_for('view_workload'))
    return redirect(url_for('alogin'))


@app.route('/leave_details/<int:faculty_id>', methods=['GET'])
def leave_details(faculty_id):
    cursor = mydb.cursor(dictionary=True)
    
    # Fetch leave applications for the given faculty member
    cursor.execute('''
        SELECT leave_id, start_date, end_date, status, application_date, response_date, leave_type, allocated_leaves, taken_leaves,faculty_id
        FROM LeaveApplications
        WHERE faculty_id = %s
    ''', (faculty_id,))
    leave_applications = cursor.fetchall()

    # Fetch leave allocation details for the given faculty member
    cursor.execute('''
        SELECT month_year, total_leavecount, assigned_leavecount
        FROM MonthlyLeaveAllocations
        WHERE faculty_id = %s
    ''', (faculty_id,))
    leave_allocations = cursor.fetchall()

    cursor.close()

    return render_template('leave_details.html', leave_applications=leave_applications, leave_allocations=leave_allocations)
@app.route('/all_leave_details', methods=['GET', 'POST'])
def all_leave_details():
    if request.method == 'POST':
        faculty_id = request.form.get('faculty_id')
        
        if not faculty_id:
            return "Faculty ID is required", 400
        
        cursor = mydb.cursor(dictionary=True)

        # Fetch leave applications for the specified faculty member
        cursor.execute('''
            SELECT faculty_id, leave_id, start_date, end_date, status, application_date, response_date, leave_type, allocated_leaves, taken_leaves
            FROM LeaveApplications
            WHERE faculty_id = %s
        ''', (faculty_id,))
        leave_applications = cursor.fetchall()

        # Fetch leave allocation details for the specified faculty member
        cursor.execute('''
            SELECT faculty_id, month_year, total_leavecount, assigned_leavecount
            FROM MonthlyLeaveAllocations
            WHERE faculty_id = %s
        ''', (faculty_id,))
        leave_allocations = cursor.fetchall()

        cursor.close()

        # Group leave applications by faculty_id
        leave_applications_by_faculty = {}
        for leave in leave_applications:
            fid = leave['faculty_id']
            if fid not in leave_applications_by_faculty:
                leave_applications_by_faculty[fid] = []
            leave_applications_by_faculty[fid].append(leave)

        # Group leave allocations by faculty_id
        leave_allocations_by_faculty = {}
        for allocation in leave_allocations:
            fid = allocation['faculty_id']
            if fid not in leave_allocations_by_faculty:
                leave_allocations_by_faculty[fid] = []
            leave_allocations_by_faculty[fid].append(allocation)

        return render_template('all_leave_details.html', 
                               leave_applications_by_faculty=leave_applications_by_faculty, 
                               leave_allocations_by_faculty=leave_allocations_by_faculty)
    else:
        return render_template('all_leave_details.html', 
                               leave_applications_by_faculty={}, 
                               leave_allocations_by_faculty={})
try:
    app.run(use_reloader=True, debug=True)
except KeyboardInterrupt:
    print("Server stopped.")










