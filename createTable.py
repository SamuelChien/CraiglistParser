import MySQLdb

#Download MYSQL from http://dev.mysql.com/downloads/mysql, mysql-5.x-osx10.x-x86_64.pkg, MySQLStartupItem.pkg, MySQL.prefpane,  Start MySQL Server, vim .bash_profile with export PATH=$PATH:/usr/local/mysql/bin, sudo mkdir /var/mysql; sudo ln -s /tmp/mysql.sock /var/mysql/mysql.sock
# http://www.macminivault.com/mysql-mountain-lion/ for instruction on MySQL download
# Download MySQLdb module http://stackoverflow.com/questions/1448429/how-to-install-mysqldb-python-data-access-library-to-mysql-on-mac-os-x


# CREATE Database
#lslsdb1 = MySQLdb.connect(host="localhost",user="root",passwd="")
#cursor = db1.cursor()
#sql = 'CREATE DATABASE mydata'
#cursor.execute(sql)

#CREATE Table and Insert Table

db1 = MySQLdb.connect(host="localhost",user="root",passwd="",db="mydata")
cursor = db1.cursor()
cursor.execute ("DROP TABLE IF EXISTS cellphone_Toronto")
cursor.execute ("""
        CREATE TABLE cellphone_Toronto
        (
        PosterID        INT,
        companyID       CHAR(200),
        title           TEXT(2000),
        dateTimeString  CHAR(200),
        dateTimeInteger INT,
        location      CHAR(200),
        imageLink     CHAR(200),
        posterLink    CHAR(200),
        posterDetail  TEXT(2000),
        email         CHAR(200),
        minPrice         INT,
        dreamPrice         INT,
        lockedCompany      CHAR(200),
        phoneType     CHAR(200),
        version    CHAR(200),
        size      CHAR(200),
        color     CHAR(200), 
        phoneNumber CHAR(200),
        itemLeft INT
        )
        """)


cursor.execute ("DROP TABLE IF EXISTS Poster_Like")
cursor.execute ("""
    CREATE TABLE poster_Like
    (
    PosterID        INT,
    LikeCount         INT
    )
    """)



cursor.execute ("DROP TABLE IF EXISTS comment_Table")
cursor.execute ("""
    CREATE TABLE comment_Table
    (
    CommentID        INT,
    dateTimeString  CHAR(200),
    dateTimeInteger INT,
    commentDetail  TEXT(2000),
    commenterID         CHAR(200)
    )
    """)

cursor.execute ("DROP TABLE IF EXISTS comment_Like")
cursor.execute ("""
    CREATE TABLE comment_Like
    (
    CommentID        INT,
    LikeCount         INT
    )
    """)

cursor.execute ("DROP TABLE IF EXISTS poster_To_Comment")
cursor.execute ("""
    CREATE TABLE poster_To_Comment
    (
    PosterID        INT,
    CommentID         INT
    )
    """)

cursor.execute ("DROP TABLE IF EXISTS poster_Offer")
cursor.execute ("""
    CREATE TABLE poster_Offer
    (
    PosterID        INT,
    OfferID         INT
    )
    """)

cursor.execute ("DROP TABLE IF EXISTS offer_For_Poster")
cursor.execute ("""
    CREATE TABLE offer_For_Poster
    (
    companyID       CHAR(200),
    title           TEXT(2000),
    dateTimeString  CHAR(200),
    dateTimeInteger INT,
    location      CHAR(200),
    imageLink     CHAR(200),
    posterDetail  TEXT(2000),
    exchangeMethod     CHAR(200),
    OfferType         CHAR(200),
    TradePosterIDs      CHAR(200),
    price INT
    )
    """)

#cursor.execute ("""
#    INSERT INTO animal (name, category)
#    VALUES
#    ('snake', 'reptile'),
#    ('frog', 'amphibian'),
#    ('tuna', 'fish'),
#    ('racoon', 'mammal')
#    """)
db1.commit()
#print "Number of rows inserted: %d" % cursor.rowcount




