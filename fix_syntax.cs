using System;
using System.IO;

class Program
{
    static void Main()
    {
        string filePath = @"c:\Users\hp\OneDrive\Desktop\Raptorflow\src\pages\app\MuseChatPage.jsx";
        string content = File.ReadAllText(filePath);
        
        // Replace the problematic line
        content = content.Replace("                  )})", "                  ))");
        
        File.WriteAllText(filePath, content);
        
        Console.WriteLine("Syntax error fixed");
    }
}
