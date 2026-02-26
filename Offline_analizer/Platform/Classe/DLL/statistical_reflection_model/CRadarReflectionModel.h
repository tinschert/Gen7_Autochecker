#ifndef CRADAR_REFLECTION_MODEL_H
#define CRADAR_REFLECTION_MODEL_H

//#define NOMINMAX

#include <armadillo>

void get_variational_radar_model_coeff_from_json();

struct vrmReflection {
  double z_x{-1};
  double z_y{-1};
};

struct gmmData {
  arma::mat means;
  arma::cube covMats;
  arma::rowvec mixCoeffs;
};

class CRadarReflectionModel {
  //*********************************
  // constructor/destructor/copy/move
  //*********************************
 public:
  CRadarReflectionModel() = default;
  virtual ~CRadarReflectionModel() = default;

  //*******************************
  // methods
  //*******************************
 public:
  void init();
  void getReflections(double aspect_angle, ::std::vector<vrmReflection>& vrmLocsOut);

 public:
 private:
};

#endif  // CRADAR_REFLECTION_MODEL_H
