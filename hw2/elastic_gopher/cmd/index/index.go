package index

import (
	"elastic_gopher/cmd/index/create"
	"elastic_gopher/cmd/index/delete"
	"elastic_gopher/cmd/index/document"
	"fmt"

	"github.com/spf13/cobra"
)

var Cmd = &cobra.Command{
	Use:   "index",
	Short: "A subcommand regarding indexing",
	Long:  `A subcommand to perform indexing operations in Elasticsearch.`,
	Args:  cobra.MinimumNArgs(0),
	Run: func(cmd *cobra.Command, args []string) {
		fmt.Println("Error: Please specify a subcommand. Use --help to see available subcommands.")
		// Here you would add the logic to perform the search using the provided index and query.
	},
}

func Bind(rootCmd *cobra.Command) {
	create.Bind(Cmd)
	delete.Bind(Cmd)
	document.Bind(Cmd)
	rootCmd.AddCommand(Cmd)
}
