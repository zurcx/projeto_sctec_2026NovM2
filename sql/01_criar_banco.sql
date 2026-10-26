CREATE DATABASE IF NOT EXISTS pncp_controladoria
CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

USE pncp_controladoria;

CREATE TABLE IF NOT EXISTS dim_orgao (
    sk_orgao INT NOT NULL AUTO_INCREMENT,
    cnpj_orgao VARCHAR(20) NOT NULL,
    nome_orgao VARCHAR(255) NOT NULL,
    poder VARCHAR(50) NOT NULL,
    PRIMARY KEY (sk_orgao),
    UNIQUE KEY uk_orgao_cnpj (cnpj_orgao)
);

CREATE TABLE IF NOT EXISTS dim_fornecedor (
    sk_fornecedor INT NOT NULL AUTO_INCREMENT,
    ni_fornecedor VARCHAR(20) NOT NULL,
    nome_fornecedor VARCHAR(255) NOT NULL,
    tipo_pessoa VARCHAR(10),
    porte VARCHAR(50),
    PRIMARY KEY (sk_fornecedor),
    UNIQUE KEY uk_fornecedor_ni (ni_fornecedor)
);

CREATE TABLE IF NOT EXISTS dim_modalidade (
    sk_modalidade INT NOT NULL AUTO_INCREMENT,
    modalidade_id INT NOT NULL,
    nome_modalidade VARCHAR(100) NOT NULL,
    PRIMARY KEY (sk_modalidade),
    UNIQUE KEY uk_modalidade_id (modalidade_id)
);

CREATE TABLE IF NOT EXISTS dim_localidade (
    sk_localidade INT NOT NULL AUTO_INCREMENT,
    uf_sigla VARCHAR(2) NOT NULL,
    uf_nome VARCHAR(100) NOT NULL,
    regiao VARCHAR(50) NOT NULL,
    PRIMARY KEY (sk_localidade),
    UNIQUE KEY uk_localidade_uf (uf_sigla)
);

CREATE TABLE IF NOT EXISTS fato_item_contratado (
    sk_fato INT NOT NULL AUTO_INCREMENT,
    numero_controle_pncp VARCHAR(50) NOT NULL,
    numero_item INT NOT NULL,
    sk_orgao INT NOT NULL,
    sk_fornecedor INT NOT NULL,
    sk_modalidade INT NOT NULL,
    sk_localidade INT NOT NULL,
    data_publicacao DATE NOT NULL,
    data_homologacao DATE NULL,
    descricao_item TEXT,
    perfil_gasto VARCHAR(50) NOT NULL,
    quantidade DECIMAL(18,4) NOT NULL,
    valor_unitario_estimado DECIMAL(18,4) NOT NULL,
    valor_unitario_homologado DECIMAL(18,4) NOT NULL,
    valor_total_estimado DECIMAL(18,2) NOT NULL,
    valor_total_homologado DECIMAL(18,2) NOT NULL,
    comparavel TINYINT(1) NOT NULL DEFAULT 0,
    economia_valor DECIMAL(18,2) NULL,
    dias_ciclo INT NULL,
    PRIMARY KEY (sk_fato),
    UNIQUE KEY uk_fato_item (numero_controle_pncp, numero_item),
    CONSTRAINT fk_fato_orgao FOREIGN KEY (sk_orgao) REFERENCES dim_orgao (sk_orgao),
    CONSTRAINT fk_fato_fornecedor FOREIGN KEY (sk_fornecedor) REFERENCES dim_fornecedor (sk_fornecedor),
    CONSTRAINT fk_fato_modalidade FOREIGN KEY (sk_modalidade) REFERENCES dim_modalidade (sk_modalidade),
    CONSTRAINT fk_fato_localidade FOREIGN KEY (sk_localidade) REFERENCES dim_localidade (sk_localidade),
    CONSTRAINT chk_qtd CHECK (quantidade > 0),
    CONSTRAINT chk_vte CHECK (valor_total_estimado >= 0),
    CONSTRAINT chk_vth CHECK (valor_total_homologado >= 0)
);

-- Registros de contingência (SK = -1) para integridade referencial
INSERT IGNORE INTO dim_orgao (sk_orgao, cnpj_orgao, nome_orgao, poder)
VALUES (-1, '00000000000000', 'Não Informado', 'Não informado');

INSERT IGNORE INTO dim_fornecedor (sk_fornecedor, ni_fornecedor, nome_fornecedor, tipo_pessoa, porte)
VALUES (-1, '00000000000000', 'Não Informado', 'ND', 'Não informado');
