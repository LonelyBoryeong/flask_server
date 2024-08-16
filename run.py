from app import create_app

app = create_app()

if __name__ == "__main__":
    app.run(debug=True)  # 또는 필요에 따라 설정을 변경
