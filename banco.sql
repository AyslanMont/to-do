CREATE DATABASE db_tarefas;
USE db_tarefas;

CREATE TABLE tb_usuarios(
usu_id INT PRIMARY KEY NOT NULL AUTO_INCREMENT,
usu_nome VARCHAR(255) NOT NULL,
usu_email VARCHAR(255) NOT NULL,
usu_senha VARCHAR(200) NOT NULL
);

CREATE TABLE tb_tarefas(
tar_id INT PRIMARY KEY NOT NULL AUTO_INCREMENT,
tar_titulo VARCHAR(100) NOT NULL,
tar_desc VARCHAR(1000)  NOT NULL,
tar_data_criacao DATE NOT NULL,
tar_data_limite DATE NOT NULL,
tar_status VARCHAR(255) NOT NULL,
tar_prioridade VARCHAR(5) NOT NULL,
tar_categoria VARCHAR(10) NOT NULL,
tar_usu_id INT NOT NULL,
FOREIGN KEY(tar_usu_id) REFERENCES tb_usuarios(usu_id)
);