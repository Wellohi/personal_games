SELECT
    DIM_CLIENTE_CONSORCIO.NR_CPF_CNPJ             AS GP_CPF_CNPJ, 
    DIM_CLIENTE_CONSORCIO.DS_NM_CLI               AS GP_NOME_CLIENTE, 
    DIM_CLIENTE_CONSORCIO.DS_GRP_ECN              AS GPGRUPO_ECONÔMICO
FROM
    PRD_DWA_CNS..DIM_CLIENTE_CONSORCIO DIM_CLIENTE_CONSORCIO
GROUP BY 
    DIM_CLIENTE_CONSORCIO.NR_CPF_CNPJ, 
    DIM_CLIENTE_CONSORCIO.DS_NM_CLI, 
    DIM_CLIENTE_CONSORCIO.DS_GRP_ECN

    -- ______________________________ --

SELECT
    "Cliente"."CPF_CNPJ" AS "CPF_CNPJ_Cliente_associado", 
    "Cliente"."Nome_Cliente" AS "Nome_Cliente_Associado", 
    "Conta_Capital"."Número_CPF_CNPJ" AS "CPF_CNPJ_Cônjuge", 
    "Conta_Capital"."Nome_Cliente" AS "Nome_Cônjuge", 
    SUM("Conta_Capital"."Valor_Integralizado") AS "Valor_Integralizado"
FROM
    (
    SELECT
        "DIM_CLIENTE_VIGENTE"."NR_CPF_CNPJ" AS "CPF_CNPJ", 
        "DIM_CLIENTE_VIGENTE"."DS_NM_CLI" AS "Nome_Cliente", 
        "DIM_CLIENTE_VIGENTE"."NUMCPFCONJUGE" AS "CPF_do_Cônjuge", 
        "DIM_CLIENTE_VIGENTE"."NOMECONJUGECLIENTE" AS "Nome_do_Cônjuge"
    FROM
        "PRD_DWA_COR".."DIM_CLIENTE_VIGENTE" "DIM_CLIENTE_VIGENTE" 
    WHERE 
        NOT ( "DIM_CLIENTE_VIGENTE"."NOMECONJUGECLIENTE" IN ( 
            'NÃO INFORMADO', 
            'NAO INFORMADO', 
            'NAO SE APLICA', 
            'NÃO SE APLICA' ) ) AND
        NOT ( "DIM_CLIENTE_VIGENTE"."NUMCPFCONJUGE" IN ( 
            '-2', 
            '-1', 
            '' ) ) 
    GROUP BY 
        "DIM_CLIENTE_VIGENTE"."NR_CPF_CNPJ", 
        "DIM_CLIENTE_VIGENTE"."DS_NM_CLI", 
        "DIM_CLIENTE_VIGENTE"."NUMCPFCONJUGE", 
        "DIM_CLIENTE_VIGENTE"."NOMECONJUGECLIENTE"
    ) "Cliente"
        LEFT OUTER JOIN 
        (
        SELECT
            "DIM_CLIENTE_CCA"."NR_CPF_CNPJ" AS "Número_CPF_CNPJ", 
            "DIM_CLIENTE_CCA"."DS_NM_CLI" AS "Nome_Cliente", 
            "DIM_CLIENTE_CCA"."NUMCPFCONJUGE" AS "CPF_do_Cônjuge", 
            "DIM_CLIENTE_CCA"."NOMECONJUGECLIENTE" AS "Nome_do_Cônjuge", 
            SUM("FAT_CONTA_CAPITAL_MENSAL"."VR_TTL_IGR") AS "Valor_Integralizado", 
            "DIM_INSTITUICAO_PAD"."NR_CPR_CENTRAL" AS "Número_Central", 
            "DIM_INSTITUICAO_PAD"."NR_CPR" AS "Número_Cooperativa"
        FROM
            "PRD_DWA_CCA".."FAT_CONTA_CAPITAL_MENSAL" "FAT_CONTA_CAPITAL_MENSAL"
                INNER JOIN "PRD_DWA_CCA".."DIM_CLIENTE_CONTA_CAPITAL" "DIM_CLIENTE_CCA"
                ON "FAT_CONTA_CAPITAL_MENSAL"."SK_CLI" = "DIM_CLIENTE_CCA"."SK_CLI"
                    INNER JOIN "PRD_DWA_COR".."DIM_INSTITUICAO_PAD" "DIM_INSTITUICAO_PAD"
                    ON 
                        "DIM_INSTITUICAO_PAD"."NR_CPR" = "FAT_CONTA_CAPITAL_MENSAL"."NR_CPR" AND
                        "DIM_INSTITUICAO_PAD"."SK_INS" = "FAT_CONTA_CAPITAL_MENSAL"."SK_INS" 
        WHERE 
            NOT ( "DIM_CLIENTE_CCA"."NUMCPFCONJUGE" IN ( 
                '-2', 
                '-1' ) ) AND
            NOT ( "DIM_CLIENTE_CCA"."NOMECONJUGECLIENTE" IN ( 
                'NÃO INFORMADO', 
                'NAO INFORMADO', 
                'NAO SE APLICA', 
                'NÃO SE APLICA' ) ) AND
            "FAT_CONTA_CAPITAL_MENSAL"."VR_TTL_IGR" < 1 
        GROUP BY 
            "DIM_CLIENTE_CCA"."NR_CPF_CNPJ", 
            "DIM_CLIENTE_CCA"."DS_NM_CLI", 
            "DIM_CLIENTE_CCA"."NUMCPFCONJUGE", 
            "DIM_CLIENTE_CCA"."NOMECONJUGECLIENTE", 
            "DIM_INSTITUICAO_PAD"."NR_CPR_CENTRAL", 
            "DIM_INSTITUICAO_PAD"."NR_CPR"
        ) "Conta_Capital"
        ON "Cliente"."CPF_do_Cônjuge" = "Conta_Capital"."Número_CPF_CNPJ" 
GROUP BY 
    "Cliente"."CPF_CNPJ", 
    "Cliente"."Nome_Cliente", 
    "Conta_Capital"."Número_CPF_CNPJ", 
    "Conta_Capital"."Nome_Cliente"