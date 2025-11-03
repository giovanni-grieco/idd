package cmd

import (
	"bufio"
	"elastic_gopher/cmd/config"
	"elastic_gopher/cmd/index"
	"elastic_gopher/cmd/search"
	"fmt"
	"os"

	"github.com/spf13/cobra"
)

// Global Variable declared before the Main execution. Upon package initialization, this variable is set up.
var rootCmd = &cobra.Command{
	Use:   "elastic_gopher",
	Short: "A simple CLI for Elasticsearch operations",
	Long:  `A simple CLI application to perform basic Elasticsearch operations like creating indices, indexing documents, searching, and deleting indices.`,
	Run: func(cmd *cobra.Command, args []string) {
		fmt.Println("Welcome to Elastic Gopher")
		fmt.Println("You are now in Interactive Mode")
		fmt.Println("Interactive mode NOT YET IMPLEMENTED")
		fmt.Println("If you need help in using the tool in Non-Interactive Mode use the -h or --help option.")
		scanner := bufio.NewScanner(os.Stdin)

		for scanner.Scan() {
			fmt.Printf("Your input was: %s\n", scanner.Text())
		}
	},
}

func Execute() {
	if err := rootCmd.Execute(); err != nil {
		fmt.Fprintf(os.Stderr, "Error: %s\n", err)
		os.Exit(1)
	}
}

func init() {
	search.Bind(rootCmd)
	index.Bind(rootCmd)
	config.Bind(rootCmd)
}
