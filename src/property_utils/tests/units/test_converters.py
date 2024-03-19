from unittest import TestSuite, TextTestRunner

from unittest_extensions import TestCase, args

from property_utils.units.units import (
    RelativeTemperatureUnit,
    AbsoluteTemperatureUnit,
    LengthUnit,
    MassUnit,
    AmountUnit,
    TimeUnit,
    ElectricCurrentUnit,
    ForceUnit,
    PressureUnit,
    EnergyUnit,
    PowerUnit,
)
from property_utils.units.converters import (
    RelativeTemperatureUnitConverter,
    AbsoluteTemperatureUnitConverter,
    LengthUnitConverter,
    MassUnitConverter,
    AmountUnitConverter,
    TimeUnitConverter,
    ElectricCurrentUnitConverter,
    AliasForceUnitConverter,
    AliasPressureUnitConverter,
    AliasEnergyUnitConverter,
    AliasPowerUnitConverter,
)
from property_utils.exceptions.units.converter_types import UnitConversionError
from property_utils.tests.utils import add_to, def_load_tests


load_tests = def_load_tests("property_utils.units.converters")

converters_test_suite = TestSuite()

converters_test_suite.addTests(
    [
        (TemperatureUnitConverter_test_suite := TestSuite()),
        (AbsoluteTemperatureUnitConverter_test_suite := TestSuite()),
        (LengthUnitConverter_test_suite := TestSuite()),
        (MassUnitConverter_test_suite := TestSuite()),
        (AmountUnitConverter_test_suite := TestSuite()),
        (TimeUnitConverter_test_suite := TestSuite()),
        (ElectricCurrentUnitConverter_test_suite := TestSuite()),
        (AliasForceUnitConverter_test_suite := TestSuite()),
        (AliasPressureUnitConverter_test_suite := TestSuite()),
        (AliasEnergyUnitConverter_test_suite := TestSuite()),
        (AliasPowerUnitConverter_test_suite := TestSuite()),
    ]
)


@add_to(TemperatureUnitConverter_test_suite)
class TestTemperatureUnitConverterConvertToReference(TestCase):
    def subject(self, value, from_descriptor):
        return RelativeTemperatureUnitConverter.convert(
            value, from_descriptor, RelativeTemperatureUnit.CELCIUS
        )

    @args({"value": 300, "from_descriptor": AbsoluteTemperatureUnit.KELVIN})
    def test_from_kelvin(self):
        self.assertResultAlmost(26.85, 2)

    @args({"value": 289.23, "from_descriptor": RelativeTemperatureUnit.FAHRENHEIT})
    def test_from_fahrenheit(self):
        self.assertResultAlmost(142.905, 2)

    @args({"value": 467, "from_descriptor": AbsoluteTemperatureUnit.RANKINE})
    def test_from_rankine(self):
        self.assertResultAlmost(-13.705, 2)

    @args({"value": 467, "from_descriptor": LengthUnit.CENTI_METER})
    def test_from_invalid_descriptor(self):
        self.assertResultRaises(UnitConversionError)

    @args({"value": "231.2", "from_descriptor": AbsoluteTemperatureUnit.KELVIN})
    def test_with_invalid_value(self):
        self.assertResultRaises(UnitConversionError)


@add_to(TemperatureUnitConverter_test_suite)
class TestTemperatureUnitConverterConvertFromReference(TestCase):
    def subject(self, value, to_descriptor):
        return RelativeTemperatureUnitConverter.convert(
            value, RelativeTemperatureUnit.CELCIUS, to_descriptor
        )

    @args({"value": 100, "to_descriptor": RelativeTemperatureUnit.CELCIUS})
    def test_to_celcius(self):
        self.assertResult(100)

    @args({"value": 10, "to_descriptor": AbsoluteTemperatureUnit.KELVIN})
    def test_to_kelvin(self):
        self.assertResult(283.15)

    @args({"value": 100, "to_descriptor": RelativeTemperatureUnit.FAHRENHEIT})
    def test_to_fahrenheit(self):
        self.assertResult(212)

    @args({"value": 67.98, "to_descriptor": AbsoluteTemperatureUnit.RANKINE})
    def test_to_rankine(self):
        self.assertResultAlmost(614.03, 2)

    @args({"value": 467, "to_descriptor": LengthUnit.FOOT})
    def test_to_invalid_descriptor(self):
        self.assertResultRaises(UnitConversionError)


@add_to(AbsoluteTemperatureUnitConverter_test_suite)
class TestAbsoluteTemperatureUnitConverterConvertToReference(TestCase):
    def subject(self, value, from_descriptor):
        return AbsoluteTemperatureUnitConverter.convert(
            value, from_descriptor, AbsoluteTemperatureUnit.KELVIN
        )

    @args({"value": 300.5, "from_descriptor": AbsoluteTemperatureUnit.KELVIN})
    def test_from_kelvin(self):
        self.assertResult(300.5)

    @args({"value": 450, "from_descriptor": AbsoluteTemperatureUnit.RANKINE})
    def test_from_rankine(self):
        self.assertResultAlmost(450 / 1.8)

    @args({"value": 25, "from_descriptor": RelativeTemperatureUnit.CELCIUS})
    def test_from_celcius(self):
        self.assertResult(298.15)

    @args({"value": 212, "from_descriptor": RelativeTemperatureUnit.FAHRENHEIT})
    def test_from_fahrenheit(self):
        self.assertResultAlmost(373.15)


@add_to(AbsoluteTemperatureUnitConverter_test_suite)
class TestAbsoluteTemperatureUnitConverterConvertFromReference(TestCase):
    def subject(self, value, to_descriptor):
        return AbsoluteTemperatureUnitConverter.convert(
            value, AbsoluteTemperatureUnit.KELVIN, to_descriptor
        )

    @args({"value": 367.29, "to_descriptor": AbsoluteTemperatureUnit.KELVIN})
    def test_to_kelvin(self):
        self.assertResult(367.29)

    @args({"value": 200.50, "to_descriptor": AbsoluteTemperatureUnit.RANKINE})
    def test_to_rankine(self):
        self.assertResult(200.50 * 1.8)

    @args({"value": 10.5, "to_descriptor": RelativeTemperatureUnit.CELCIUS})
    def test_to_celcius(self):
        self.assertResult(-262.65)

    @args({"value": 400, "to_descriptor": RelativeTemperatureUnit.FAHRENHEIT})
    def test_to_fahrenheit(self):
        self.assertResultAlmost(260.33)


@add_to(LengthUnitConverter_test_suite)
class TestLengthUnitConverterConvertToReference(TestCase):
    def subject(self, value, from_descriptor):
        return LengthUnitConverter.convert(value, from_descriptor, LengthUnit.METER)

    @args({"value": 283, "from_descriptor": LengthUnit.MILLI_METER})
    def test_from_milli_meter(self):
        self.assertResultAlmost(0.283, 3)

    @args({"value": 156, "from_descriptor": LengthUnit.CENTI_METER})
    def test_from_centi_meter(self):
        self.assertResult(1.56)

    @args({"value": 29.013, "from_descriptor": LengthUnit.METER})
    def test_from_meter(self):
        self.assertResult(29.013)

    @args({"value": 9.51, "from_descriptor": LengthUnit.KILO_METER})
    def test_from_kilo_meter(self):
        self.assertResult(9_510)

    @args({"value": 56, "from_descriptor": LengthUnit.INCH})
    def test_from_inch(self):
        self.assertResultAlmost(56 * 2.54 / 100, 3)

    @args({"value": 23.2, "from_descriptor": LengthUnit.FOOT})
    def test_from_foot(self):
        self.assertResultAlmost(23.2 * 12 * 2.54 / 100, 3)

    @args({"value": 2.4, "from_descriptor": LengthUnit.YARD})
    def test_from_yard(self):
        self.assertResult(2.4 / 1.094)

    @args({"value": 2.01, "from_descriptor": LengthUnit.MILE})
    def test_from_mile(self):
        self.assertResult(2.01 * 1609)

    @args({"value": 5.08, "from_descriptor": LengthUnit.NAUTICAL_MILE})
    def test_from_nautical_mile(self):
        self.assertResult(5.08 * 1852)


@add_to(LengthUnitConverter_test_suite)
class TestLengthUnitConverterConvertFromReference(TestCase):
    def subject(self, value, to_descriptor):
        return LengthUnitConverter.convert(value, LengthUnit.METER, to_descriptor)

    @args({"value": 0.09862, "to_descriptor": LengthUnit.MILLI_METER})
    def test_to_milli_meter(self):
        self.assertResult(98.62)

    @args({"value": 2.02, "to_descriptor": LengthUnit.CENTI_METER})
    def test_to_centi_meter(self):
        self.assertResult(202)

    @args({"value": 5, "to_descriptor": LengthUnit.METER})
    def test_to_meter(self):
        self.assertResult(5)

    @args({"value": 25.4, "to_descriptor": LengthUnit.KILO_METER})
    def test_to_kilo_meter(self):
        self.assertResultAlmost(0.0254, 4)

    @args({"value": 3.3, "to_descriptor": LengthUnit.INCH})
    def test_to_inch(self):
        self.assertResultAlmost(3.3 * 100 / 2.54, 2)

    @args({"value": 15, "to_descriptor": LengthUnit.FOOT})
    def test_to_foot(self):
        self.assertResultAlmost(15 * 100 / 2.54 / 12, 2)

    @args({"value": 5, "to_descriptor": LengthUnit.YARD})
    def test_to_yard(self):
        self.assertResult(5 * 1.094)

    @args({"value": 2_000, "to_descriptor": LengthUnit.MILE})
    def test_to_mile(self):
        self.assertResultAlmost(2000 / 1609, 4)

    @args({"value": 562, "to_descriptor": LengthUnit.NAUTICAL_MILE})
    def test_to_nautical_mile(self):
        self.assertResult(562 / 1852)


@add_to(MassUnitConverter_test_suite)
class TestMassUnitConverterConvertToReference(TestCase):
    def subject(self, value, from_descriptor):
        return MassUnitConverter.convert(value, from_descriptor, MassUnit.KILO_GRAM)

    @args({"value": 12, "from_descriptor": MassUnit.MILLI_GRAM})
    def test_from_milli_gram(self):
        self.assertResult(0.000012)

    @args({"value": 101, "from_descriptor": MassUnit.GRAM})
    def test_from_gram(self):
        self.assertResult(0.101)

    @args({"value": 67.398, "from_descriptor": MassUnit.KILO_GRAM})
    def test_from_kilo_gram(self):
        self.assertResult(67.398)

    @args({"value": 2.37, "from_descriptor": MassUnit.METRIC_TONNE})
    def test_from_metric_tonne(self):
        self.assertResult(2_370)

    @args({"value": 20, "from_descriptor": MassUnit.POUND})
    def test_from_pound(self):
        self.assertResultAlmost(20 / 2.205, 2)


@add_to(MassUnitConverter_test_suite)
class TestMassUnitConverterConvertFromReference(TestCase):
    def subject(self, value, to_descriptor):
        return MassUnitConverter.convert(value, MassUnit.KILO_GRAM, to_descriptor)

    @args({"value": 0.013, "to_descriptor": MassUnit.MILLI_GRAM})
    def test_to_milli_gram(self):
        self.assertResult(13_000)

    @args({"value": 2, "to_descriptor": MassUnit.GRAM})
    def test_to_gram(self):
        self.assertResult(2_000)

    @args({"value": 2.60, "to_descriptor": MassUnit.KILO_GRAM})
    def test_to_kilo_gram(self):
        self.assertResult(2.60)

    @args({"value": 690, "to_descriptor": MassUnit.METRIC_TONNE})
    def test_to_metric_tonne(self):
        self.assertResultAlmost(0.690, 3)

    @args({"value": 0.84, "to_descriptor": MassUnit.POUND})
    def test_to_pound(self):
        self.assertResult(0.84 * 2.205)


@add_to(AmountUnitConverter_test_suite)
class TestAmountUnitConverterConvertToReference(TestCase):
    def subject(self, value, from_descriptor):
        return AmountUnitConverter.convert(value, from_descriptor, AmountUnit.MOL)

    @args({"value": 90, "from_descriptor": AmountUnit.MOL})
    def test_from_mol(self):
        self.assertResult(90)

    @args({"value": 45, "from_descriptor": AmountUnit.KILO_MOL})
    def test_from_kilo_mol(self):
        self.assertResult(45_000)


@add_to(AmountUnitConverter_test_suite)
class TestAmountUnitConverterConvertFromReference(TestCase):
    def subject(self, value, to_descriptor):
        return AmountUnitConverter.convert(value, AmountUnit.MOL, to_descriptor)

    @args({"value": 23.333, "to_descriptor": AmountUnit.MOL})
    def test_to_mol(self):
        self.assertResult(23.333)

    @args({"value": 29, "to_descriptor": AmountUnit.KILO_MOL})
    def test_to_kilo_mol(self):
        self.assertResult(0.029)


@add_to(TimeUnitConverter_test_suite)
class TestTimeUnitConverterConvertToReference(TestCase):
    def subject(self, value, from_descriptor):
        return TimeUnitConverter.convert(value, from_descriptor, TimeUnit.SECOND)

    @args({"value": 98.01, "from_descriptor": TimeUnit.MILLI_SECOND})
    def test_from_milli_second(self):
        self.assertResultAlmost(0.09801, 5)

    @args({"value": 222, "from_descriptor": TimeUnit.SECOND})
    def test_from_second(self):
        self.assertResultAlmost(222)

    @args({"value": 2.5, "from_descriptor": TimeUnit.MINUTE})
    def test_from_minute(self):
        self.assertResult(150)

    @args({"value": 0.25, "from_descriptor": TimeUnit.HOUR})
    def test_from_hour(self):
        self.assertResult(15 * 60)

    @args({"value": 7, "from_descriptor": TimeUnit.DAY})
    def test_from_day(self):
        self.assertResult(7 * 24 * 60 * 60)

    @args({"value": 0.3, "from_descriptor": TimeUnit.WEEK})
    def test_from_week(self):
        self.assertResultAlmost(0.3 * 7 * 24 * 60 * 60, 1)

    @args({"value": 2, "from_descriptor": TimeUnit.MONTH})
    def test_from_month(self):
        self.assertResultAlmost(2 * (365 / 12) * 24 * 60 * 60, 1)

    @args({"value": 1.5, "from_descriptor": TimeUnit.YEAR})
    def test_from_year(self):
        self.assertResultAlmost(1.5 * 365 * 24 * 60 * 60, 1)


@add_to(TimeUnitConverter_test_suite)
class TestTimeUnitConverterConvertFromReference(TestCase):
    def subject(self, value, to_descriptor):
        return TimeUnitConverter.convert(value, TimeUnit.SECOND, to_descriptor)

    @args({"value": 3, "to_descriptor": TimeUnit.MILLI_SECOND})
    def test_to_milli_second(self):
        self.assertResult(3_000)

    @args({"value": 2.3, "to_descriptor": TimeUnit.SECOND})
    def test_to_second(self):
        self.assertResult(2.3)

    @args({"value": 100, "to_descriptor": TimeUnit.MINUTE})
    def test_to_minute(self):
        self.assertResult(100.0 / 60)

    @args({"value": 1000, "to_descriptor": TimeUnit.HOUR})
    def test_to_hour(self):
        self.assertResult(1000.0 / 60 / 60)

    @args({"value": 5672, "to_descriptor": TimeUnit.DAY})
    def test_to_day(self):
        self.assertResult(5672.0 / 60 / 60 / 24)

    @args({"value": 56_000, "to_descriptor": TimeUnit.WEEK})
    def test_to_week(self):
        self.assertResultAlmost(56_000 / 60 / 60 / 24 / 7)

    @args({"value": 476_032, "to_descriptor": TimeUnit.MONTH})
    def test_to_month(self):
        self.assertResultAlmost(476_032 / 60 / 60 / 24 / (365 / 12))

    @args({"value": 1_090_382, "to_descriptor": TimeUnit.YEAR})
    def test_to_year(self):
        self.assertResultAlmost(1_090_382 / 365 / 24 / 60 / 60)


@add_to(ElectricCurrentUnitConverter_test_suite)
class TestElectricCurrentUnitConvertConvertToReference(TestCase):
    def subject(self, value, from_descriptor):
        return ElectricCurrentUnitConverter.convert(
            value, from_descriptor, ElectricCurrentUnit.AMPERE
        )

    @args({"value": 5800, "from_descriptor": ElectricCurrentUnit.MILLI_AMPERE})
    def test_from_milli_ampere(self):
        self.assertResult(5.800)

    @args({"value": 3.1415, "from_descriptor": ElectricCurrentUnit.AMPERE})
    def test_from_ampere(self):
        self.assertResult(3.1415)

    @args({"value": 0.32, "from_descriptor": ElectricCurrentUnit.KILO_AMPERE})
    def test_from_kilo_ampere(self):
        self.assertResult(320)


@add_to(ElectricCurrentUnitConverter_test_suite)
class TestElectricCurrentUnitConverterConvertFromReference(TestCase):
    def subject(self, value, to_descriptor):
        return ElectricCurrentUnitConverter.convert(
            value, ElectricCurrentUnit.AMPERE, to_descriptor
        )

    @args({"value": 0.29, "to_descriptor": ElectricCurrentUnit.MILLI_AMPERE})
    def test_to_milli_ampere(self):
        self.assertResult(290)

    @args({"value": 46720, "to_descriptor": ElectricCurrentUnit.AMPERE})
    def test_to_ampere(self):
        self.assertResult(46720)

    @args({"value": 326.9, "to_descriptor": ElectricCurrentUnit.KILO_AMPERE})
    def test_to_kilo_ampere(self):
        self.assertResultAlmost(0.326, delta=0.001)


@add_to(AliasForceUnitConverter_test_suite)
class TestAliasForceUnitConverterConvertToReference(TestCase):
    def subject(self, value, from_descriptor):
        return AliasForceUnitConverter.convert(value, from_descriptor, ForceUnit.NEWTON)

    @args({"value": 1450, "from_descriptor": ForceUnit.NEWTON})
    def test_from_newton(self):
        self.assertResult(1450)

    @args({"value": 15_000, "from_descriptor": ForceUnit.DYNE})
    def test_from_dyne(self):
        self.assertResultAlmost(0.15, 5)


@add_to(AliasForceUnitConverter_test_suite)
class TestAliasForceUnitConverterConvertFromReference(TestCase):
    def subject(self, value, to_descriptor):
        return AliasForceUnitConverter.convert(value, ForceUnit.NEWTON, to_descriptor)

    @args({"value": 284.008, "to_descriptor": ForceUnit.NEWTON})
    def test_to_newton(self):
        self.assertResult(284.008)

    @args({"value": 28, "to_descriptor": ForceUnit.DYNE})
    def test_to_dyne(self):
        self.assertResult(2_800_000)


@add_to(AliasPressureUnitConverter_test_suite)
class TestAliasPressureUnitConverterConvertToReference(TestCase):
    def subject(self, value, from_descriptor):
        return AliasPressureUnitConverter.convert(
            value, from_descriptor, PressureUnit.BAR
        )

    @args({"value": 2500, "from_descriptor": PressureUnit.MILLI_BAR})
    def test_from_millibar(self):
        self.assertResult(2.500)

    @args({"value": 17.45, "from_descriptor": PressureUnit.BAR})
    def test_from_bar(self):
        self.assertResult(17.45)

    @args({"value": 29, "from_descriptor": PressureUnit.PSI})
    def test_from_psi(self):
        self.assertResultAlmost(1.999, 3)

    @args({"value": 243_000, "from_descriptor": PressureUnit.PASCAL})
    def test_from_pascal(self):
        self.assertResult(2.43)

    @args({"value": 345.6, "from_descriptor": PressureUnit.KILO_PASCAL})
    def test_from_kilo_pascal(self):
        self.assertResultAlmost(3.456, 3)

    @args({"value": 25, "from_descriptor": PressureUnit.MEGA_PASCAL})
    def test_from_mega_pascal(self):
        self.assertResult(250)


@add_to(AliasPressureUnitConverter_test_suite)
class TestAliasPressureUnitConverterConvertFromReference(TestCase):
    def subject(self, value, to_descriptor):
        return AliasPressureUnitConverter.convert(
            value, PressureUnit.BAR, to_descriptor
        )

    @args({"value": 32.78, "to_descriptor": PressureUnit.MILLI_BAR})
    def test_to_millibar(self):
        self.assertResult(32_780)

    @args({"value": 4, "to_descriptor": PressureUnit.PSI})
    def test_to_psi(self):
        self.assertResultAlmost(58.0152, 4)

    @args({"value": 3.56, "to_descriptor": PressureUnit.PASCAL})
    def test_to_pascal(self):
        self.assertResult(356000)

    @args({"value": 0.55, "to_descriptor": PressureUnit.KILO_PASCAL})
    def test_to_kilo_pascal(self):
        self.assertResultAlmost(55.0, 2)

    @args({"value": 2.7, "to_descriptor": PressureUnit.MEGA_PASCAL})
    def test_to_mega_pascal(self):
        self.assertResult(0.27)


@add_to(AliasEnergyUnitConverter_test_suite)
class TestAliasEnergyUnitConverterConvertToReference(TestCase):
    def subject(self, value, from_descriptor):
        return AliasEnergyUnitConverter.convert(
            value, from_descriptor, EnergyUnit.JOULE
        )

    @args({"value": 10.32, "from_descriptor": EnergyUnit.JOULE})
    def test_from_joule(self):
        self.assertResult(10.32)

    @args({"value": 23, "from_descriptor": EnergyUnit.KILO_JOULE})
    def test_from_kilo_joule(self):
        self.assertResult(23_000)

    @args({"value": 0.0505, "from_descriptor": EnergyUnit.MEGA_JOULE})
    def test_from_mega_joule(self):
        self.assertResult(50_500)

    @args({"value": 1.016, "from_descriptor": EnergyUnit.GIGA_JOULE})
    def test_from_giga_joule(self):
        self.assertResultAlmost(1_016_000_000, 1)

    @args({"value": 520, "from_descriptor": EnergyUnit.CALORIE})
    def test_from_calorie(self):
        self.assertResult(520 * 4.184)

    @args({"value": 666, "from_descriptor": EnergyUnit.KILO_CALORIE})
    def test_from_kilo_calorie(self):
        self.assertResult(666 * 1000 * 4.184)

    @args({"value": 0.3, "from_descriptor": EnergyUnit.BTU})
    def test_from_btu(self):
        self.assertResult(0.3 * 1055)

    @args({"value": 5.8291e16, "from_descriptor": EnergyUnit.ELECTRONVOLT})
    def test_from_electronvolt(self):
        self.assertResultAlmost(5.8291e16 / 6.242e18)

    @args({"value": 2, "from_descriptor": EnergyUnit.WATTHOUR})
    def test_from_watthour(self):
        self.assertResult(7200)

    @args({"value": 7, "from_descriptor": EnergyUnit.KILO_WATTHOUR})
    def test_from_kilo_watthour(self):
        self.assertResultAlmost(7 * 3600 * 1000)


@add_to(AliasEnergyUnitConverter_test_suite)
class TestAliasEnergyUnitConverterConvertFromReference(TestCase):
    def subject(self, value, to_descriptor):
        return AliasEnergyUnitConverter.convert(value, EnergyUnit.JOULE, to_descriptor)

    @args({"value": 10.32, "to_descriptor": EnergyUnit.JOULE})
    def test_to_joule(self):
        self.assertResult(10.32)

    @args({"value": 5_000, "to_descriptor": EnergyUnit.KILO_JOULE})
    def test_to_kilo_joule(self):
        self.assertResult(5)

    @args({"value": 67_032, "to_descriptor": EnergyUnit.MEGA_JOULE})
    def test_to_mega_joule(self):
        self.assertResult(0.067032)

    @args({"value": 232_001, "to_descriptor": EnergyUnit.GIGA_JOULE})
    def test_to_giga_joule(self):
        self.assertResultAlmost(0.000232001, 9)

    @args({"value": 10, "to_descriptor": EnergyUnit.CALORIE})
    def test_to_calorie(self):
        self.assertResult(10 / 4.184)

    @args({"value": 3_200, "to_descriptor": EnergyUnit.KILO_CALORIE})
    def test_to_kilo_calorie(self):
        self.assertResultAlmost(3200 / 4.184 / 1000, 4)

    @args({"value": 5_000, "to_descriptor": EnergyUnit.BTU})
    def test_to_btu(self):
        self.assertResult(5000 / 1055)

    @args({"value": 5.27002e-16, "to_descriptor": EnergyUnit.ELECTRONVOLT})
    def test_to_electronvolt(self):
        self.assertResultAlmost(5.27002e-16 * 6.242e18)

    @args({"value": 8_000, "to_descriptor": EnergyUnit.WATTHOUR})
    def test_to_watthour(self):
        self.assertResult(8000 / 3600)

    @args({"value": 100_000, "to_descriptor": EnergyUnit.KILO_WATTHOUR})
    def test_to_kilo_watthour(self):
        self.assertResultAlmost(100_000 / 3600 / 1000)


@add_to(AliasPowerUnitConverter_test_suite)
class TestAliasPowerUnitConverterConvertToReference(TestCase):
    def subject(self, value, from_descriptor):
        return AliasPowerUnitConverter.convert(value, from_descriptor, PowerUnit.WATT)

    @args({"value": 10.02, "from_descriptor": PowerUnit.WATT})
    def test_from_watt(self):
        self.assertResult(10.02)

    @args({"value": 0.032, "from_descriptor": PowerUnit.KILO_WATT})
    def test_from_kilo_watt(self):
        self.assertResult(32)

    @args({"value": 22, "from_descriptor": PowerUnit.MEGA_WATT})
    def test_from_watt(self):
        self.assertResult(22_000_000)

    @args({"value": 5.0201, "from_descriptor": PowerUnit.GIGA_WATT})
    def test_from_watt(self):
        self.assertResult(5_020_100_000)


@add_to(AliasPowerUnitConverter_test_suite)
class TestAliasPowerUnitConverterConvertFromReference(TestCase):
    def subject(self, value, to_descriptor):
        return AliasPowerUnitConverter.convert(value, PowerUnit.WATT, to_descriptor)

    @args({"value": 29, "to_descriptor": PowerUnit.WATT})
    def test_to_watt(self):
        self.assertResult(29)

    @args({"value": 55.5, "to_descriptor": PowerUnit.KILO_WATT})
    def test_to_kilo_watt(self):
        self.assertResult(0.0555)

    @args({"value": 17_001.9, "to_descriptor": PowerUnit.MEGA_WATT})
    def test_to_mega_watt(self):
        self.assertResult(0.0170019)

    @args({"value": 5, "to_descriptor": PowerUnit.GIGA_WATT})
    def test_to_giga_watt(self):
        self.assertResult(5e-9)


if __name__ == "__main__":
    runner = TextTestRunner()
    runner.run(converters_test_suite)
