
from app import create_app, db
from app.models import FirmyTyp, Firmy
from sqlalchemy import text

app = create_app()

def migrate_firmy_typ():
    with app.app_context():
        try:
            # Sprawdź czy tabela tymczasowa istnieje i usuń ją jeśli tak
            db.session.execute(text("DROP TABLE IF EXISTS FIRMY_TYP_TEMP"))
            db.session.commit()
            
            # Utwórz tabelę tymczasową
            db.session.execute(text("""
                CREATE TABLE FIRMY_TYP_TEMP (
                    ID_FIRMY_TYP INTEGER PRIMARY KEY AUTOINCREMENT,
                    Typ_firmy TEXT
                )
            """))
            
            # Skopiuj dane
            db.session.execute(text("""
                INSERT INTO FIRMY_TYP_TEMP (Typ_firmy)
                SELECT Typ_firmy FROM FIRMY_TYP
            """))
            
            # Stwórz mapowanie starych ID na nowe
            old_to_new = {}
            results = db.session.execute(text("""
                SELECT ft.ID_FIRMY_TYP as old_id, ftt.ID_FIRMY_TYP as new_id, ftt.Typ_firmy
                FROM FIRMY_TYP ft
                JOIN FIRMY_TYP_TEMP ftt ON ft.Typ_firmy = ftt.Typ_firmy
            """)).fetchall()
            
            for row in results:
                old_to_new[row.old_id] = row.new_id
            
            # Zaktualizuj referencje w tabeli FIRMY
            for old_id, new_id in old_to_new.items():
                db.session.execute(
                    text("UPDATE FIRMY SET ID_FIRMY_TYP = :new_id WHERE ID_FIRMY_TYP = :old_id"),
                    {"new_id": new_id, "old_id": old_id}
                )
            
            # Usuń starą tabelę i zmień nazwę nowej
            db.session.execute(text("DROP TABLE FIRMY_TYP"))
            db.session.execute(text("ALTER TABLE FIRMY_TYP_TEMP RENAME TO FIRMY_TYP"))
            
            db.session.commit()
            print("Migracja zakończona pomyślnie!")
            
        except Exception as e:
            db.session.rollback()
            print(f"Wystąpił błąd: {str(e)}")
            raise

if __name__ == "__main__":
    migrate_firmy_typ()
