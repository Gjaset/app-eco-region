from app.core.seguridad import hash_password, verify_password


def test_passwords_are_hashed_and_verifiable():
    password = "una-clave-segura"
    hashed = hash_password(password)

    assert hashed != password
    assert verify_password(password, hashed)
    assert not verify_password("otra-clave", hashed)