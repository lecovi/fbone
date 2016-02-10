# -*- coding: utf-8 -*-

import os

from flask import Blueprint, render_template, send_from_directory, abort
from flask import current_app as APP
from flask.ext.login import login_required, current_user

from .models import User


student = Blueprint('student', __name__, url_prefix='/student')


@student.route('/')
@login_required
def index():
    if not current_user.is_authenticated:
        abort(403)
    return render_template('student/index.html', user=current_user)


@student.route('/<int:student_id>/profile')
def profile(student_id):
    student = User.get_by_id(student_id)
    return render_template('student/profile.html', student=student)


@student.route('/<int:student_id>/avatar/<path:filename>')
@login_required
def avatar(student_id, filename):
    dir_path = os.path.join(APP.config['UPLOAD_FOLDER'], 'student_%s' % student_id)
    return send_from_directory(dir_path, filename, as_attachment=True)
