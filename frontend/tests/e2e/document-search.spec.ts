import fs from "node:fs";
import path from "node:path";
import { expect, test } from "@playwright/test";

const fixturePath = path.resolve(
  process.cwd(),
  "..",
  "backend",
  "tests",
  "fixtures",
  "files",
  "valid.docx",
);

test("upload, index, search, and return document result", async ({ request }) => {
  test.skip(!fs.existsSync(fixturePath), "Нужны фикстуры из QA-02 (#41)");

  const login = await request.post("/auth/demo", {
    data: { role: "admin" },
  });
  expect(login.ok()).toBeTruthy();
  const { access_token: token } = await login.json();

  const upload = await request.post("/documents/upload", {
    headers: { Authorization: `Bearer ${token}` },
    multipart: {
      file: {
        name: "valid.docx",
        mimeType:
          "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        buffer: fs.readFileSync(fixturePath),
      },
    },
  });
  expect(upload.status()).toBe(201);
  const document = await upload.json();

  await expect
    .poll(
      async () => {
        const response = await request.get(`/documents/${document.id}`, {
          headers: { Authorization: `Bearer ${token}` },
        });
        return response.ok() ? (await response.json()).status : "missing";
      },
      { timeout: 10_000 },
    )
    .toBe("done");

  const search = await request.get("/search", {
    headers: { Authorization: `Bearer ${token}` },
    params: { q: "тестовый" },
  });
  expect(search.ok()).toBeTruthy();
  const results = await search.json();

  expect(results.total).toBeGreaterThan(0);
  expect(results.results[0].doc).toBe("valid.docx");
  expect(results.results[0].text.toLowerCase()).toContain("тест");
});
