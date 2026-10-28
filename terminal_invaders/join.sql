SELECT
    Cliente.CPF_CNPJ                                AS CPF_CNPJ_Cliente_associado, 
    Cliente.Nome_Cliente                            AS Nome_Cliente_Associado, 
    Conta_Capital.Número_CPF_CNPJ                   AS CPF_CNPJ_Cônjuge, 
    Conta_Capital.Nome_Cliente                      AS Nome_Cônjuge, 
    SUM(Conta_Capital.Valor_Integralizado)          AS Valor_Integralizado,
    DIM_CLIENTE_CONSORCIO.NR_CPF_CNPJ               AS GP_CPF_CNPJ, 
    DIM_CLIENTE_CONSORCIO.DS_NM_CLI                 AS GP_NOME_CLIENTE, 
    DIM_CLIENTE_CONSORCIO.DS_GRP_ECN                AS GPGRUPO_ECONÔMICO

FROM
    (
    SELECT
        dim_cliente_vigente.NR_CPF_CNPJ AS CPF_CNPJ, 
        dim_cliente_vigente.DS_NM_CLI AS Nome_Cliente, 
        dim_cliente_vigente.NUMCPFCONJUGE AS CPF_do_Cônjuge, 
        dim_cliente_vigente.NOMECONJUGECLIENTE AS Nome_do_Cônjuge
    FROM
        netezza_prodconscobranca.prd_dwa_cor.dim_cliente_vigente 
    WHERE 
        NOT ( dim_cliente_vigente.NOMECONJUGECLIENTE IN ( 
            'NÃO INFORMADO', 
            'NAO INFORMADO', 
            'NAO SE APLICA', 
            'NÃO SE APLICA' ) ) AND
        NOT ( dim_cliente_vigente.NUMCPFCONJUGE IN ( 
            '-2', 
            '-1', 
            '' ) ) 
    GROUP BY 
        dim_cliente_vigente.NR_CPF_CNPJ, 
        dim_cliente_vigente.DS_NM_CLI, 
        dim_cliente_vigente.NUMCPFCONJUGE, 
        dim_cliente_vigente.NOMECONJUGECLIENTE
    ) Cliente
        LEFT OUTER JOIN 
        (
        SELECT
            DIM_CLIENTE_CCA.NR_CPF_CNPJ AS Número_CPF_CNPJ, 
            DIM_CLIENTE_CCA.DS_NM_CLI AS Nome_Cliente, 
            DIM_CLIENTE_CCA.NUMCPFCONJUGE AS CPF_do_Cônjuge, 
            DIM_CLIENTE_CCA.NOMECONJUGECLIENTE AS Nome_do_Cônjuge, 
            SUM(FAT_CONTA_CAPITAL_MENSAL.VR_TTL_IGR) AS Valor_Integralizado, 
            DIM_INSTITUICAO_PAD.NR_CPR_CENTRAL AS Número_Central, 
            DIM_INSTITUICAO_PAD.NR_CPR AS Número_Cooperativa
        FROM
            netezza_prodconscobranca.prd_dwa_cca.fat_associado_conta_capital_mensal FAT_CONTA_CAPITAL_MENSAL
                INNER JOIN netezza_prodconscobranca.prd_dwa_cca.dim_cliente_conta_capital DIM_CLIENTE_CCA
                ON FAT_CONTA_CAPITAL_MENSAL.SK_CLI = DIM_CLIENTE_CCA.SK_CLI
                    INNER JOIN netezza_prodconscobranca.prd_dwa_cor.dim_instituicao_pad DIM_INSTITUICAO_PAD
                    ON 
                        DIM_INSTITUICAO_PAD.NR_CPR = FAT_CONTA_CAPITAL_MENSAL.NR_CPR AND
                        DIM_INSTITUICAO_PAD.SK_INS = FAT_CONTA_CAPITAL_MENSAL.SK_INS 
        WHERE 
            NOT ( DIM_CLIENTE_CCA.NUMCPFCONJUGE IN ( 
                '-2', 
                '-1' ) ) AND
            NOT ( DIM_CLIENTE_CCA.NOMECONJUGECLIENTE IN ( 
                'NÃO INFORMADO', 
                'NAO INFORMADO', 
                'NAO SE APLICA', 
                'NÃO SE APLICA' ) ) AND
            FAT_CONTA_CAPITAL_MENSAL.VR_TTL_IGR < 1 
        GROUP BY 
            DIM_CLIENTE_CCA.NR_CPF_CNPJ, 
            DIM_CLIENTE_CCA.DS_NM_CLI, 
            DIM_CLIENTE_CCA.NUMCPFCONJUGE, 
            DIM_CLIENTE_CCA.NOMECONJUGECLIENTE, 
            DIM_INSTITUICAO_PAD.NR_CPR_CENTRAL, 
            DIM_INSTITUICAO_PAD.NR_CPR
        ) Conta_Capital
        ON Cliente.CPF_do_Cônjuge = Conta_Capital.Número_CPF_CNPJ 

INNER JOIN
    netezza_prodconscobranca.prd_dwa_cns.dim_cliente_consorcio DIM_CLIENTE_CONSORCIO
    ON Cliente.CPF_CNPJ = DIM_CLIENTE_CONSORCIO.NR_CPF_CNPJ

GROUP BY 
    Cliente.CPF_CNPJ, 
    Cliente.Nome_Cliente, 
    Conta_Capital.Número_CPF_CNPJ, 
    Conta_Capital.Nome_Cliente.
    DIM_CLIENTE_CONSORCIO.NR_CPF_CNPJ, 
    DIM_CLIENTE_CONSORCIO.DS_NM_CLI, 
    DIM_CLIENTE_CONSORCIO.DS_GRP_ECN
