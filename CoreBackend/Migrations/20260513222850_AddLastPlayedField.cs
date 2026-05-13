using System;
using Microsoft.EntityFrameworkCore.Migrations;

#nullable disable

namespace CoreBackend.Migrations
{
    /// <inheritdoc />
    public partial class AddLastPlayedField : Migration
    {
        /// <inheritdoc />
        protected override void Up(MigrationBuilder migrationBuilder)
        {
            migrationBuilder.AddColumn<DateTime>(
                name: "LastPlayed",
                table: "GameRecords",
                type: "timestamp with time zone",
                nullable: true);
        }

        /// <inheritdoc />
        protected override void Down(MigrationBuilder migrationBuilder)
        {
            migrationBuilder.DropColumn(
                name: "LastPlayed",
                table: "GameRecords");
        }
    }
}
