using Microsoft.EntityFrameworkCore.Migrations;

#nullable disable

namespace CoreBackend.Migrations
{
    /// <inheritdoc />
    public partial class AddAchievementsFields : Migration
    {
        /// <inheritdoc />
        protected override void Up(MigrationBuilder migrationBuilder)
        {
            migrationBuilder.AddColumn<int>(
                name: "AchievementsTotal",
                table: "GameRecords",
                type: "integer",
                nullable: true);

            migrationBuilder.AddColumn<int>(
                name: "AchievementsUnlocked",
                table: "GameRecords",
                type: "integer",
                nullable: true);

            migrationBuilder.AddColumn<string>(
                name: "RecentAchievementsJson",
                table: "GameRecords",
                type: "text",
                nullable: true);
        }

        /// <inheritdoc />
        protected override void Down(MigrationBuilder migrationBuilder)
        {
            migrationBuilder.DropColumn(
                name: "AchievementsTotal",
                table: "GameRecords");

            migrationBuilder.DropColumn(
                name: "AchievementsUnlocked",
                table: "GameRecords");

            migrationBuilder.DropColumn(
                name: "RecentAchievementsJson",
                table: "GameRecords");
        }
    }
}
