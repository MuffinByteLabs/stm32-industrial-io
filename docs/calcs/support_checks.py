"""I reproduce capture-support bounds; this does not validate the built circuit."""
from itertools import product
import json


def divider_bounds(top, bottom, thresholds, bias):
    # Independent tolerance plus worst 25 C excursion at 25 ppm/C.
    rerr = 0.001 + 25e-6 * 25
    values = [(v * (1 + rt / rb) + ib * rt)
              for v, rt, rb, ib in product(thresholds,
                  (top * (1-rerr), top * (1+rerr)),
                  (bottom * (1-rerr), bottom * (1+rerr)), (-bias, bias))]
    return [min(values), max(values)]


def calculate():
    rerr, referr = .001 + 25e-6*25, .0015 + 30e-6*25
    def negative(thresholds):
        v = [(node * (1+rn/rp) - ref * rn/rp + ib*rn)
             for node, rn, rp, ref, ib in product(thresholds,
                (18500*(1-rerr),18500*(1+rerr)),
                (68100*(1-rerr),68100*(1+rerr)),
                (2.5*(1-referr),2.5*(1+referr)),(-15e-9,15e-9))]
        return [min(v), max(v)]
    usb_min=25230/(61.9*1.01)**1.016
    usb_max=22980/(61.9*.99)**.94
    result={
        'scope':'Arithmetic and documented assumptions; pin/net/layout/firmware/bench checks pending',
        'resistor_error_fraction':rerr,
        'field_uv_rising_release_v':divider_bounds(210000,10000,(.396,.404),25e-9),
        'field_uv_falling_assert_v':divider_bounds(210000,10000,(.387,.400),25e-9),
        'field_ov_rising_assert_v':divider_bounds(770000,10000,(.396,.404),15e-9),
        'field_ov_falling_release_v':divider_bounds(770000,10000,(.387,.400),15e-9),
        'analog15_uv_rising_release_v':divider_bounds(320000,10000,(.396,.404),25e-9),
        'analog15_uv_falling_assert_v':divider_bounds(320000,10000,(.387,.400),25e-9),
        'analog15_ov_rising_assert_v':divider_bounds(400000,10000,(.396,.404),15e-9),
        'analog15_ov_falling_release_v':divider_bounds(400000,10000,(.387,.400),15e-9),
        'reference_uv_rising_release_v':divider_bounds(50000,10000,(.396,.404),25e-9),
        'negative_bias_loss_assert_v':negative((.396,.404)),
        'negative_bias_recovery_v':negative((.387,.400)),
        'negative_node_reference_absent_normal_bias_v':-.27*68100/(68100+18500),
        'usb_fault_limit_ma':[usb_min,usb_max],
        'eeprom_rise_time_200pf_s':.8473*4700*200e-12,
        'hse_pll':{'input_hz':8000000,'m':2,'n':72,'r':2,'q':6,
                   'core_hz':144000000,'usb_fdcan_hz':48000000},
        'watchdog_timeout_ms':[170,230],
        'watchdog_service_interval_ms':50,
    }
    # These checks concern useful design margins, not implementation equivalence.
    assert result['field_uv_rising_release_v'][1] < 9
    assert result['field_ov_falling_release_v'][0] > 30
    assert result['negative_bias_loss_assert_v'][1] < -.15
    assert result['negative_bias_recovery_v'][0] > -.23
    assert usb_max < 500
    assert result['eeprom_rise_time_200pf_s'] < 1e-6
    return result


if __name__ == '__main__':
    print(json.dumps(calculate(),indent=2))
