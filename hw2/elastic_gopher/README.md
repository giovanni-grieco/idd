# elastic_gopher

A CLI Go client for Elasticsearch.

## Usage

```bash
elastic_gopher [command] [subcommand] [flags]
```

## Commands
- `search`: Perform a search query on an Elasticsearch index.
- `index`: Index a new document into an Elasticsearch index.
### SEARCH
```bash
elastic_gopher search <index_name> --fields <field1>='<value1>',<field2>='<value2>'
```
or using raw JSON:
```bash
elastic_gopher search <index_name> '{query_json}'
```

### INDEX
WIP

## Setup Environment
Before running the commands, ensure you have set the following environment variables:
```bash
go mod init elastic_gopher
go mod tidy
```

## Build
To build the project, run:
```bash
go build
```

## Install
To install the project, run:
```bash
go install
```
