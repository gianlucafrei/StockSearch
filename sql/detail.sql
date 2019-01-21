SELECT
    *
FROM
    stocksearch."ShareData" AS v,
    stocksearch."Calendar" AS c
WHERE
    v."day" = c."day"
    AND v."key"='SIX/AT0000676903CHF'
    AND v."day" >= 508
    AND v."day" <= 1073
ORDER BY v."day";

