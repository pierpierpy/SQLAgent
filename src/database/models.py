from sqlalchemy import Column, String, Integer
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    fullname = Column(String)
    email = Column(String, unique=True, index=True)
    password = Column(String)


class Report(Base):
    __tablename__ = "report"

    id = Column(Integer, primary_key=True, index=True)
    Anno_Mese = Column("Anno Mese", String)
    Compagnia = Column(String)
    Ramo_di_Bilancio = Column("Ramo di Bilancio", String)
    Desc_Ramo_di_Bilancio = Column("Desc. Ramo di Bilancio", String)
    Settore_Business = Column("Settore Business", String)
    Settore = Column(String)
    Premi_Contabilizzati = Column("Premi Contabilizzati", String)
    Premi_Incassati = Column("Premi Incassati", String)
    Prodotto = Column(String)
    Desc_Prodotto = Column("Desc. Prodotto", String)
    Canale_Commerciale = Column("Canale Commerciale", String)
    Area = Column(String)
    Regione_attuale = Column("Regione attuale", String)


class MessageStore(Base):
    __tablename__ = "message_store_super_agent"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column("session_id", String)
    message = Column("message", String)


class SQLMessageStore(Base):
    __tablename__ = "message_store_sql_agent"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column("session_id", String)
    message = Column("message", String)


class ConversationOwnership(Base):
    __tablename__ = "conversation_owners"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column("user_id", String)
    conversation_id = Column("session_id", String)
    number_of_messages = Column("number_of_messages", Integer)
