using NUnit.Framework;
using SingletonExample;

namespace SingletonTest
{
    public class Tests
    {
        [SetUp]
        public void Setup()
        {
        }

        [Test]
        public void Test_Tanken()
        {
            // Arrange
            Auto auto = Auto.Instance;
            bool expectedMotor = false;
            bool expectedTank = false;

            // Act
            bool actualMotor = auto.isLeeg();
            bool actualTank = auto.staatAan();

            // Assert
            Assert.AreEqual(expectedMotor, actualMotor);
            Assert.AreEqual(expectedTank, actualTank);
        }

        [Test]
        public void Test_Rijden()
        {
            // Arrange
            Auto auto = Auto.Instance;
            bool expectedMotor = true;
            bool expectedTank = true;

            // Act
            bool actualMotor = auto.isLeeg();
            bool actualTank = auto.staatAan();

            // Assert
            Assert.AreEqual(expectedMotor, actualMotor);
            Assert.AreEqual(expectedTank, actualTank);
        }

        [Test]
        public void Test_Aanzetten()
        {

            // Arrange
            Auto auto = Auto.Instance;
            bool expectedMotor = true;
            bool expectedTank = false;

            // Act
            bool actualMotor = auto.isLeeg();
            bool actualTank = auto.staatAan();

            // Assert
            Assert.AreEqual(expectedMotor, actualMotor);
            Assert.AreEqual(expectedTank, actualTank);
        }

        [Test]
        public void Test_Uitzetten()
        {
            // Arrange
            Auto auto = Auto.Instance;
            bool expectedMotor = false;
            bool expectedTank = true;

            // Act
            bool actualMotor = auto.isLeeg();
            bool actualTank = auto.staatAan();

            // Assert
            Assert.AreEqual(expectedMotor, actualMotor);
            Assert.AreEqual(expectedTank, actualTank);
        }
    }
}