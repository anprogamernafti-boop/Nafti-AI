#!/usr/bin/env python3
"""
Script pour vérifier et régénérer les certificats SSL pour la reconnaissance vocale
"""
import os
import ssl
import datetime
from cryptography import x509
from cryptography.x509.oid import NameOID
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.backends import default_backend

def check_certificate():
    """Vérifie si le certificat existe et est valide"""
    cert_file = 'server.crt'
    key_file = 'server.key'

    if not os.path.exists(cert_file) or not os.path.exists(key_file):
        print("❌ Certificats manquants")
        return False

    try:
        # Charger le certificat
        with open(cert_file, 'rb') as f:
            cert_data = f.read()

        cert = x509.load_pem_x509_certificate(cert_data, default_backend())

        # Vérifier la date d'expiration
        if cert.not_valid_after < datetime.datetime.utcnow():
            print("❌ Certificat expiré")
            return False

        # Vérifier le sujet
        subject = cert.subject
        common_name = subject.get_attributes_for_oid(NameOID.COMMON_NAME)[0].value

        print(f"✅ Certificat valide pour: {common_name}")
        print(f"   Expire le: {cert.not_valid_after}")
        return True

    except Exception as e:
        print(f"❌ Erreur certificat: {e}")
        return False

def generate_certificate():
    """Génère un nouveau certificat auto-signé"""
    print("🔄 Génération d'un nouveau certificat SSL...")

    # Générer la clé privée
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
        backend=default_backend()
    )

    # Créer le certificat
    subject = issuer = x509.Name([
        x509.NameAttribute(NameOID.COUNTRY_NAME, "FR"),
        x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, "France"),
        x509.NameAttribute(NameOID.LOCALITY_NAME, "Paris"),
        x509.NameAttribute(NameOID.ORGANIZATION_NAME, "Nafti AI"),
        x509.NameAttribute(NameOID.COMMON_NAME, "localhost"),
    ])

    cert = x509.CertificateBuilder().subject_name(
        subject
    ).issuer_name(
        issuer
    ).public_key(
        private_key.public_key()
    ).serial_number(
        x509.random_serial_number()
    ).not_valid_before(
        datetime.datetime.utcnow()
    ).not_valid_after(
        datetime.datetime.utcnow() + datetime.timedelta(days=365)
    ).add_extension(
        x509.SubjectAlternativeName([
            x509.DNSName("localhost"),
            x509.DNSName("127.0.0.1"),
        ]),
        critical=False,
    ).sign(private_key, hashes.SHA256(), default_backend())

    # Sauvegarder la clé privée
    with open('server.key', 'wb') as f:
        f.write(private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        ))

    # Sauvegarder le certificat
    with open('server.crt', 'wb') as f:
        f.write(cert.public_bytes(serialization.Encoding.PEM))

    print("✅ Nouveau certificat généré")
    print("ℹ️  Pensez à accepter le certificat dans votre navigateur")

if __name__ == "__main__":
    try:
        from cryptography import x509
    except ImportError:
        print("❌ Module 'cryptography' requis. Installez-le avec: pip install cryptography")
        exit(1)

    if check_certificate():
        print("✅ Certificat OK")
    else:
        generate_certificate()