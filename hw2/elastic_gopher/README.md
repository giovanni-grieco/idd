# elastic_gopher

A CLI Go client for Elasticsearch.  
Provides simple commands to create/delete/list indices, index documents (single or folder), and run searches.

## Requirements
- Go 1.25+ (or compatible)

## Build & Install

```bash
go mod tidy
go build
# or install to \$GOBIN
go install
```

## CLI Usage

General form:
```bash
elastic_gopher [command] [subcommand] [flags]
```

Top-level commands:
- `search` — perform a search query on an index
- `index` — index documents (single document or a folder)
- `create` — create an index using the provided mapping
- `delete` — delete an index
- `list` — list indices

### SEARCH

Search by key/value fields:
```bash
elastic_gopher search <index_name> --fields title='Hello',body='world'
```

Search using raw JSON (pass a full Elasticsearch query as a single positional argument):
```bash
elastic_gopher search <index_name> '{ "query": { "match": { "body": "hello" } } }'
```

Notes:
- The `--fields` flag accepts comma-separated `key='value'` pairs.
- Passing a raw JSON query as the second positional argument will be used directly as the request body.

### INDEX (documents)

Index a single document via `--fields`:
```bash
elastic_gopher index document my-index --fields title='My Title',body='My content'
```

Index all files under a folder (recursively). Each file becomes a document where:
- `title` = filename without extension
- `body` = file content

```bash
elastic_gopher index document my-index --path /path/to/folder
# or the provided helper script:
./index_path.sh my-index /path/to/folder
```

Behavior:
- Flags are optional; the command enforces that at least one of `--fields` or `--path` (or a raw JSON document) is provided.
- Bulk Indexing isn't implemented yet; documents are indexed one-by-one.

### CREATE / DELETE / LIST

Create an index using the provided mapping in `index_mappings.json`:
```bash
elastic_gopher index create my-index --mappings "$(cat index_mappings.json)"
```
Where `test_index` is the desired index name and index_mappings.json contains the mapping definition.
You can also specify raw JSON directly via the `--mappings` flag.
```bash
elastic_gopher index create my-index --mappings '{"mappings":{"properties":{"my-field":{"type":"some-type"}}}}}'
```

Delete an index:
```bash
elastic_gopher index delete my-index
```

List indices:
```bash
elastic_gopher index ls
```

### Example workflow

1. Create the index (applies mapping):
```bash
./create_index.sh my-index
```

2. Index sample files:
```bash
./index_path.sh my-index ./sample_files
```

3. Search:
```bash
elastic_gopher search my-index --fields title='hello'
# or
elastic_gopher search my-index '{ "query": { "match": { "body": "goodbye" } } }'
```

## Index mapping

A mapping example is provided in `index_mappings.json`. Modify as needed for your use case.
Here's another minimal example:
```json
{
  "mappings": {
    "properties": {
      "title": {
        "type": "text"
      },
      "body": {
        "type": "text"
      }
    }
  }
}
```

## Scripts

Provided convenience scripts in the project root:
- `create_index.sh` — create index called `test_index` with `index_mappings.json`
- `delete_index.sh` — delete index called `test_index`
- `index_path.sh` — index all files in `sample_files` folder into `test_index`
- `index_document.sh` — index a single document using flags
- `list_index.sh` — list indices
- `search_files.sh` — an example of searching the indexed documents