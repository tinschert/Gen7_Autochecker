#include "MathLibrary.hpp"
#include <iostream>
using namespace std;

int main(){
    MathLibrary::TargetCalculation calculation_class;
    MathLibrary::LocationCloud locations;
    double location_array[4];
    double dist_x,dist_y;

    calculation_class.calculate_ref_point(1.5,2,4,20,20,0,18,18,0);
    calculation_class.calculate_Locations(4,1.5);
    locations = calculation_class.get_Locations();

    for(int i = 0; i<sizeof(location_array); i++){
        switch(i){
            case 0:
                dist_x = locations.dx_mid;
                dist_y = locations.dy_mid;
                break;
            case 1:
                dist_x = locations.dx_left;
                dist_y = locations.dy_left;
                break;
            case 2:
                dist_x = locations.dx_right;
                dist_y = locations.dy_right;
                break;
            case 3:
                dist_x = locations.dx_far;
                dist_y = locations.dy_far;
                break;
        }
        location_array[i] = calculation_class.calc_radial_distance(dist_x, dist_y);
    }
    cout << "1. Location = " << location_array[0] << endl;
    cout << "2. Location = " << location_array[1] << endl;
    cout << "3. Location = " << location_array[2] << endl;
    cout << "4. Location = " << location_array[3] << endl;

    return 0;
}