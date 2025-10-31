package config

import (
	"fmt"

	"github.com/spf13/cobra"
)

var Cmd = &cobra.Command{
	Use:   "configure",
	Short: "Configure elastic_gopher",
	Long:  "Configure elastic_gopher by specifying client and backend settings",
	Run: func(cmd *cobra.Command, args []string) {
		fmt.Println("To be implemented")
		return
	},
}

func Bind(rootCmd *cobra.Command) {
	rootCmd.AddCommand(Cmd)
}
