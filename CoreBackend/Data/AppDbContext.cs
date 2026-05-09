using Microsoft.EntityFrameworkCore;
using CoreBackend.Models;

namespace CoreBackend.Data;

public class AppDbContext : DbContext
{
    public AppDbContext(DbContextOptions<AppDbContext> options) : base(options) { }

    public DbSet<UserProfile> UserProfiles { get; set; }
    public DbSet<GameRecord> GameRecords { get; set; }

    protected override void OnModelCreating(ModelBuilder modelBuilder)
    {
        modelBuilder.Entity<UserProfile>()
            .HasIndex(u => new { u.Platform, u.UserId })
            .IsUnique();

        modelBuilder.Entity<UserProfile>()
            .HasMany(u => u.Games)
            .WithOne(g => g.UserProfile)
            .HasForeignKey(g => g.UserProfileId)
            .OnDelete(DeleteBehavior.Cascade);
    }
}
