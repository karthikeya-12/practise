from objects_orm import get_db_session, Retrieve, Checkpoints


with get_db_session() as session:
    # user = Retrieve(id=2, message={"role": "AI"})
    # session.add(user)
    # session.commit()
    # users = session.query(Retrieve).all()
    users = session.query(Retrieve).filter_by(id=2).first()
    codes = session.query(Checkpoints).all()
    print(type(users))
    print(users.id, users.message)
    for i in codes:
        print(i.id, i.name)
    # for i, m in enumerate(users):
    #     print(f"User {i} and his data is: {m.id}\n____________________________________________________________________\nUser {i}\n_____________________________________________\n{m.message}")
# import qrcode

# qr = qrcode.QRCode()

# link = "https://outlook.office.com/mail/"

# loc = "qrimage.png"

# qr.add_data(link)
# image = qr.make_image()
# image.save(loc)
