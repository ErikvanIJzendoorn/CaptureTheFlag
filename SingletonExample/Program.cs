using System;

namespace SingletonExample
{
    class Program
    {
        static void Main(string[] args)
        {
            // Nieuwe instantie kan niet aangemaakt worden
            //Auto kanNiet = new Auto();

            // Haal de bestaande instantie op
            Auto auto = Auto.Instance;
            
            // Doe dingen met de auto
            auto.Tanken();
            auto.AanzettenAuto();
            auto.RijdentotBijnaLeeg();
        }
    }
}
