SELECT 
    STOJOU.ITMREF_0 AS Article, 
    ITMMASTER.TSICOD_0 AS Type_Statistique_0,
    ITMMASTER.TSICOD_1 AS Type_Statistique_1,
    ITMMASTER.TSICOD_2 AS Type_Statistique_2,
    ITMMASTER.TSICOD_3 AS Type_Statistique_3,
    ITMMASTER.TSICOD_4 AS Type_Statistique_4,
    STOJOU.VCRTYP_0 AS Type_Piece,
    STOJOU.TRSTYP_0 AS Type_Mouvement,
    STOJOU.QTYPCU_0 AS Quantite_PCU,
    STOJOU.QTYSTU_0 AS Quantite_STU,
    STOJOU.IPTDAT_0 AS Date_Mouvement,
    STOJOU.STOFCY_0 AS Site_Stockage,
    STOJOU.LOC_0 AS Emplacement,
    STOJOU.PCU_0 AS Unité_Controle,
    STOJOU.STU_0 AS Unité_Stockage,
    STOJOU.BPRNUM_0 AS Client_Fournisseur,
    STOJOU.LOT_0 AS Lot
FROM STOJOU
LEFT JOIN ITMMASTER ON STOJOU.ITMREF_0 = ITMMASTER.ITMREF_0
WHERE 
    STOJOU.IPTDAT_0 >= DATEADD(month, -12, GETDATE())  -- Filtre sur les 12 derniers mois
--	AND STOJOU.STOFCY_0='AGR'
ORDER BY 
    STOJOU.IPTDAT_0 DESC;
