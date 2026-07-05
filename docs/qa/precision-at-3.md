# QA-05 Precision@3

## Method

Metric: `Precision@3 = relevant_results_in_top_3 / 3`.

Run each query through `GET /api/v1/search?q=<query>` after loading the QA fixture corpus. Mark a result as relevant when the document and snippet match the expected topic.

## Golden Queries

| # | Query | Expected relevant topic | Top-3 expectation | P@3 |
| ---: | --- | --- | --- | ---: |
| 1 | тестовый документ | Basic valid DOCX/PDF fixture | At least 1 relevant result in top 3 | pending |
| 2 | нестандартные шрифты | Fancy PDF/DOCX fixture | At least 1 relevant result in top 3 | pending |
| 3 | пустой документ | Empty fixture handling | Empty files should not appear as relevant text results | pending |
| 4 | битый файл | Corrupted fixture handling | Corrupted files should not appear as successful search hits | pending |
| 5 | учебная практика | Practice-defense materials | Practice-related document in top 3 | pending |
| 6 | лабораторная работа | Lab materials | Lab-related document in top 3 | pending |
| 7 | расписание занятий | Schedule materials | Schedule-related document in top 3 | pending |
| 8 | очередь на защиту | Queue/practice materials | Queue-related document in top 3 | pending |
| 9 | алгоритм | Technical lecture materials | Algorithm-related document in top 3 | pending |
| 10 | инженерия качества | Technical lecture materials | Engineering/QA document in top 3 | pending |

## Summary

| Total queries | Max relevant@3 | Actual relevant@3 | Precision@3 |
| ---: | ---: | ---: | ---: |
| 10 | 30 | pending | pending |

## Reporting Rule

Attach the raw search responses or screenshots from `/search` to the final QA run notes. If a query has fewer than three total results, compute precision against three slots and leave missing slots as non-relevant.
