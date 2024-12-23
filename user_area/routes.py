from flask import render_template, redirect, url_for
from flask_login import login_required, current_user
from . import user_bp
from app.models import Transaction

@user_bp.route("/transactions")
@login_required
def transactions():
    if current_user.role != "user":
        return redirect(url_for("admin_bp.dashboard"))
    txs = Transaction.query.filter_by(user_id=current_user.id).order_by(Transaction.id.desc()).all()
    return render_template("transaction_list.html", transactions=txs)
