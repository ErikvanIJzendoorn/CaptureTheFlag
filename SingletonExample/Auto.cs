using System;
using System.Collections.Generic;
using System.Text;

namespace SingletonExample
{
    public class Auto
    {
        // Maak een auto aan - dit is de enige die je hebt
        public static Auto Instance { get; } = new Auto();

        private bool tankLeeg;
        private bool motorAan;

        private Auto()
        {
            tankLeeg = true;
            motorAan = false;
        }

        public void Tanken()
        {
            // Tank moet leeg zijn en auto mag niet aanstaan
            if(isLeeg())
            {
                Console.WriteLine("Ik heb de auto getankt.");
                tankLeeg = false;
            } else
            {
                throw new Exception("Tank is niet leeg.");
            }
        }

        public void RijdentotBijnaLeeg()
        {
            // Tank moet vol zijn en auto moet aanstaan
            if(!isLeeg() && staatAan())
            {
                Console.WriteLine("Ik ben braaf naar school gegaan vandaag.");
                tankLeeg = true;
            }
            else
            {
                throw new Exception("Tank is leeg of auto staat uit.");
            }
        }

        public void AanzettenAuto()
        {
            // Tank moet vol zij en de auto mag nog niet aanstaan
            if(!isLeeg() && !staatAan())
            {
                Console.WriteLine("Ik zet de auto aan.");
                motorAan = true;
            }
            else
            {
                throw new Exception("Tank is leeg of auto staat aan.");
            }
        }

        public bool isLeeg()
        {
            return tankLeeg;
        }

        public bool staatAan()
        {
            return motorAan;
        }
    }
}
