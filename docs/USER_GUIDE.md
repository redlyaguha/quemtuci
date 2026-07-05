# User Guide

## Login

Open the application and choose one of the demo roles:

- Student: search documents, view queues, join or leave available queues.
- Teacher: create queues, manage queue members, close queues.
- Admin: upload and delete documents, monitor indexed content.

For MTUCI/TECH login, paste the personal token into the login form. The token is sent to the backend only.

## Documents

Admins can upload PDF and DOCX files from the documents page.

Upload rules:

- Allowed formats: PDF, DOCX.
- Maximum size: 20 MB.
- Empty or corrupted files are rejected or marked with an error status.

After upload, a document moves through these statuses:

- `uploading`
- `indexing`
- `done`
- `error`

When indexing is complete, the document becomes available in search.

## Search

Use the knowledge base page to search indexed documents.

Search results show:

- document name;
- document type;
- page number;
- relevance;
- highlighted text fragment.

The frontend paginates results by 10 items. Search history is available from the search page when the backend endpoint is enabled.

## Queues

Students can:

- open the queues page;
- filter queues by status;
- join an open queue;
- leave a queue before completion;
- see their current position.

Teachers can:

- create a queue;
- reorder students;
- remove a student from a queue;
- mark a student as completed;
- close a queue.

The queue object returned by the backend should always be treated as the source of truth after mutations.

## Practice Defense Queue

Teachers can create a practice defense queue from the queues page. If the backend endpoint is unavailable, the frontend opens the queue creation form with prefilled practice-defense fields.

## Profile And Integration

The profile page shows:

- user name and role;
- group or department;
- Telegram ID when available;
- MTUCI/TECH integration status;
- notification preferences.

Users can sync or disconnect MTUCI/TECH integration when the backend endpoints are available.

## Troubleshooting

If login fails, retry demo login first to verify the frontend session flow.

If uploaded documents do not appear in search:

1. Check that the status is `done`.
2. Verify that Elasticsearch is running.
3. Retry the query with a word that is present in the uploaded document.

If queues do not update immediately, refresh the page. Live queue updates are planned as polling or websocket integration.
