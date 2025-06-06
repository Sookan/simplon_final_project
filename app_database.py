import psycopg2
import os

class App_DB:
    def __init__(self):
        self.__dbname = 'app_project'
        self.__user = 'postgres'
        self.__password = 'postgres'
        self.__host = 'localhost'
        self.__port = '5432'
        self.conn = psycopg2.connect(dbname =self.__dbname, user =self.__user,
                              password = self.__password,host=self.__host, port = self.__port)

    def check_user_password(self, email, password):
        with self.conn.cursor() as cur:
            cur.execute("""
                with is_confirm_user as (
                SELECT user_id
                ,(password = crypt(%s,password)) as responce
                ,email
                FROM ref_user
                WHERE email = %s
                )
            
            , create_token as (
                SELECT user_id
                    ,CASE WHEN responce THEN crypt(md5(random()::text),gen_salt('bf',8)) ELSE null END as token
                    ,email
                FROM is_confirm_user
                
            ) 
            , insert_token_if_valid as (
                INSERT into user_token (user_id,token)
                SELECT user_id,token
                FROM create_token
                WHERE token is not null
            )
            
            SELECT *
            FROM create_token
            """, (password, email))
            self.conn.commit()
            return cur.fetchone()

    def check_user_token(self, user_id, token):
        with self.conn.cursor() as cur:
            query = """
                SELECT user_id, true as is_valid  
                FROM user_token
                where user_id = %s
                AND token= %s
                AND (EXTRACT(SECOND FROM CURRENT_TIMESTAMP - created_at ) - expire <= 0);
            """
            cur.execute(query, (user_id, token))
            return cur.fetchone()

    def delete_user_token(self, user_id, token):
        with self.conn.cursor() as cur:
            query = """
                WITH is_valide_user as  (
                SELECT user_id, true as is_valid  
                FROM user_token
                where user_id = %s
                AND token= %s
                AND (EXTRACT(SECOND FROM CURRENT_TIMESTAMP - created_at ) - expire <= 0)
                )
                
                DELETE FROM user_token 
                WHERE user_id = (SELECT user_id FROM is_valide_user)
                """
            cur.execute(query,(user_id, token))
            self.conn.commit()
        return None

    def get_user_fav(self, user_id, token):
        with self.conn.cursor() as cur:
            query = """
                WITH is_valide_user as  (
                SELECT user_id, true as is_valid  
                FROM user_token
                where user_id = %s
                AND token= %s
                AND (EXTRACT(SECOND FROM CURRENT_TIMESTAMP - created_at ) - expire <= 0)
                )

                SELECT fav FROM user_favorite 
                WHERE user_id =  (SELECT user_id FROM is_valide_user)
                """
            cur.execute(query, (user_id, token))
            return cur.fetchone()

    def delete_user_fav(self, user_id, token):
        with self.conn.cursor() as cur:
            query = """
                WITH is_valide_user as  (
                SELECT user_id, true as is_valid  
                FROM user_token
                where user_id = %s
                AND token= %s
                AND (EXTRACT(SECOND FROM CURRENT_TIMESTAMP - created_at ) - expire <= 0)
                )

                DELETE FROM user_favorite 
                WHERE user_id =  (SELECT user_id FROM is_valide_user)
                """
            cur.execute(query, (user_id, token))
            self.conn.commit()
        return None

    def change_user_fav(self, user_id, token, fav):
        with self.conn.cursor() as cur:
            query = """
                WITH is_valide_user as  (
                SELECT user_id, true as is_valid  
                FROM user_token
                where user_id = %s
                AND token= %s
                AND (EXTRACT(SECOND FROM CURRENT_TIMESTAMP - created_at ) - expire <= 0)
                )
                
                , new_fav as (
                select %s as fav
                )
                , delete_fav as (
                    DELETE FROM user_favorite 
                    WHERE user_id =  (SELECT user_id FROM is_valide_user)
                )
                
                , insert_fav as (
                    INSERT into user_favorite (user_id, fav)
                    VALUES  ((SELECT user_id FROM is_valide_user), (SELECT fav FROM new_fav))
                )
                
                Select fav from new_fav
                """
            cur.execute(query, (user_id, token, fav))
            self.conn.commit()
        return None







