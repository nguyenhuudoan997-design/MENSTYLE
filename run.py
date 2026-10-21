"""
run.py
Điểm khởi chạy ứng dụng MENSTYLE.
"""

from app import create_app

app = create_app()


if __name__ == "__main__":
    app.run(debug=True)
