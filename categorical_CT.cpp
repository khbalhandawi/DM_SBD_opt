/*-------------------------------------------------------------------*/
/*            Example of a problem with categorical variables        */
/*-------------------------------------------------------------------*/
/*                                                                   */
/*  . portfolio problem with 3 assets                                */
/*                                                                   */
/*  . NOMAD is used in library mode                                  */
/*                                                                   */
/*  . the number of variables can be 3,5, or 7, depending on the     */
/*    number of assets considered in the portfolio                   */
/*                                                                   */
/*  . variables are of the form (n t0 v0 t1 v1 t2 v2) where n is the */
/*    number of assets, ti is the type of an asset, and vi is the    */
/*    money invested in this asset                                   */
/*                                                                   */
/*  . categorical variables are n and the ti's                       */
/*                                                                   */
/*  . with a $10,000 budget, the problem consists in minimizing      */
/*    some measure of the risk and of the revenue                    */
/*                                                                   */
/*  . two classes are defined:                                       */
/*                                                                   */
/*    1. My_Evaluator, wich inherits from the NOMAD class Evaluator, */
/*       in order to define the problem via the virtual function     */
/*       eval_x()                                                    */
/*                                                                   */
/*    2. My_Extended_Poll, which inherits from the NOMAD class       */
/*       Extended_Poll, in order to define the categorical           */
/*       variables neighborhoods, via the virtual function           */
/*       construct_extended_points()                                 */
/*                                                                   */
/*  . My_Extended_Poll also defines 3 signatures, for the solutions  */
/*    with 3, 5, and 7 variables                                     */
/*-------------------------------------------------------------------*/
/*  . compile the scalar version with 'make'                         */
/*  . compile the parallel version with 'make mpi'                   */
/*-------------------------------------------------------------------*/
/*  . execute the scalar version with './categorical'                */
/*  . execute the parallel version with 'mpirun -np p ./categorical' */
/*    with p > 1                                                     */
/*-------------------------------------------------------------------*/
#include "nomad.hpp"
#include <sstream>
#include <iterator>
#include <iostream>
#include <vector>

using namespace std;
//using namespace NOMAD;

/*----------------------------------------*/
/*           support functions            */
/*----------------------------------------*/
// This function splits a delimlited string into vector of doubles
vector<double> split_string(std::string line)
{
	std::string input = line;
	istringstream ss(input);
	std:: string value;
	double value_db;

	std::vector<double> out_vector;
	while (getline(ss, value, ','))
	{
		value_db = atof(value.c_str()); // convert to float
		out_vector.push_back(value_db); // Vector of floats
		// cout << token << '\n';
	}

	return out_vector;
}
//****************End of split_stringe funtion****************

// This function reads a csv delimlited file
vector< vector<double> >  read_csv_file(string filename)
{
	ifstream file(filename); // declare file stream: http://www.cplusplus.com/reference/iostream/ifstream/
	std::string line, value;
	std::vector<double> line_vec;
	std::vector<double> concept, i1, i2, i3, i4, n_f_th;
	std::vector< vector<double> > array_grid;

	while (file.good())
	{
		getline(file, line, '\n'); // read a string until next comma: http://www.cplusplus.com/reference/string/getline/
		line_vec = split_string(line);
		concept.push_back((line_vec[1]));
		i1.push_back(line_vec[2]);
		i2.push_back(line_vec[3]);
		i3.push_back(line_vec[4]);
		i4.push_back(line_vec[5]);
		n_f_th.push_back(line_vec[32]);
	}
	array_grid = { concept, i1, i2, i3, i4, n_f_th };
	return array_grid;
}
//****************End of CSV READ funtion****************

void print_vector(const vector<int> & other_types) {

	ostringstream oss;

	if (!other_types.empty())
	{
		// Convert all but the last element to avoid a trailing ","
		copy(other_types.begin(), other_types.end() - 1,
			ostream_iterator<int>(oss, ","));

		// Now add the last element with no delimiter
		oss << other_types.back();
	}

	cout << oss.str() << endl;

}

#define USE_SURROGATE false

/*----------------------------------------*/
/*               the problem              */
/*----------------------------------------*/
class My_Evaluator : public NOMAD::Evaluator
{
public:
	My_Evaluator ( const NOMAD::Parameters & p ) :
    Evaluator ( p ) {}
	
	~My_Evaluator ( void ) {}
	
	bool eval_x (NOMAD::Eval_Point   & x          ,
				 const NOMAD::Double & h_max      ,
				 bool         & count_eval   ) const;
};

/*--------------------------------------------------*/
/*  user class to define categorical neighborhoods  */
/*--------------------------------------------------*/
class My_Extended_Poll : public NOMAD::Extended_Poll
{
	
private:
	
	// signatures for 1, 2, 3 or 4 assets:
	NOMAD::Signature * _s1, * _s2, * _s3, * _s4;

public:
	
	// constructor:
	My_Extended_Poll (NOMAD::Parameters & );
	
	// destructor:
	virtual ~My_Extended_Poll ( void ) { delete _s1; delete _s2; delete _s3; delete _s4; }
	
	// construct the extended poll points:
	virtual void construct_extended_points ( const NOMAD::Eval_Point & );
	
};

/*------------------------------------------*/
/*            NOMAD main function           */
/*------------------------------------------*/
int main ( int argc , char ** argv )
{
	
	// NOMAD initializations:
	NOMAD::begin ( argc , argv );
	
	// display:
	NOMAD::Display out ( cout );
	out.precision (NOMAD::DISPLAY_PRECISION_STD );

	// check the number of processess:
#ifdef USE_MPI
	if ( Slave::get_nb_processes() < 2 )
	{
		if ( Slave::is_master() )
			cerr << "usage: \'mpirun -np p ./categorical\' with p>1"
			<< endl;
		end();
		return EXIT_FAILURE;
	}
#endif
	
	try
	{
		
		// parameters creation:
		NOMAD::Parameters p ( out );
		
		vector<NOMAD::bb_output_type> bbot(1);
		bbot[0] = NOMAD::OBJ; // objective

		// initial point
		NOMAD::Point x0(3, 1);
		x0[0] = 1;   // 1 deposit
		x0[1] = 0;   // wave concept
		x0[2] = 1;   // deposit type 1
		p.set_X0(x0);

		NOMAD::Point lb(3);
		NOMAD::Point ub(3);
		// Categorical variables don't need bounds
		lb[1] = 0; ub[1] = 3;
        lb[2] = 0; ub[2] = 3;

        //p.set_DISPLAY_DEGREE ( NOMAD::FULL_DISPLAY );

		p.set_DIMENSION (3);
		//p.set_MAX_BB_EVAL(400);
		//p.set_INT_POLL_DIR_TYPE(NOMAD::INT_POLL_DIR);
		//p.set_EXTENDED_POLL_ENABLED(true);
		//NOMAD::Point msize(3);
		//msize[0] = msize[1] = msize[2] = 20;
		//p.set_MIN_MESH_SIZE(msize);
		//p.set_INITIAL_MESH_SIZE(msize);

		p.set_BB_OUTPUT_TYPE ( bbot );
		
		// categorical variables:
		p.set_BB_INPUT_TYPE ( 0 , NOMAD::CATEGORICAL);
		p.set_BB_INPUT_TYPE ( 1 , NOMAD::INTEGER );
		p.set_BB_INPUT_TYPE ( 2 , NOMAD::INTEGER );

		p.set_DISABLE_MODELS();
		p.set_INITIAL_MESH_SIZE(2.0);

		p.set_LOWER_BOUND ( lb );
		p.set_UPPER_BOUND ( ub );
		
		p.set_DISPLAY_STATS ( "bbe ( sol ) obj" );
		p.set_MAX_BB_EVAL ( 200 );

		// extended poll trigger:
		p.set_EXTENDED_POLL_TRIGGER ( 10 , false );
		
		// parameters validation:
		p.check();

		// custom point to debug ev and ep:
		NOMAD::Eval_Point xt(3, 1);
		xt[0] = 1;
		xt[1] = 0;
		xt[2] = 1;

		NOMAD::Double hmax = 1;
		bool count = false;

		// custom evaluator creation:
		My_Evaluator ev ( p );

		ev.eval_x(xt, hmax, count);
		xt.display_eval(cout); // Debug evaluator

		// extended poll:
		My_Extended_Poll ep ( p );

		ep.construct_extended_points(xt); // debug extended poll

		// algorithm creation and execution:
		NOMAD::Mads mads ( p , &ev , &ep , NULL , NULL );
		mads.run();
	}
	catch ( exception & e ) {
		string error = string ( "NOMAD has been interrupted: " ) + e.what();
		if (NOMAD::Slave::is_master() )
			cerr << endl << error << endl << endl;
	}
	
	
	NOMAD::Slave::stop_slaves ( out );
	NOMAD::end();
	
	return EXIT_SUCCESS;
}

/*----------------------------------------------------*/
/*                         eval_x                     */
/*----------------------------------------------------*/
bool My_Evaluator::eval_x(NOMAD::Eval_Point   & x,
	const NOMAD::Double & h_max,
	bool         & count_eval) const
{
	NOMAD::Double f; // objective function
	//--------------------------------------------------------------//
	// Read from data file
	
	count_eval = false;

	string input_file = "varout_opt_log.log";
	vector< vector<double> > input_array = read_csv_file(input_file); // Make sure there are no empty lines !!

	vector<double> concept, i1, i2, i3, i4, n_f_th;
	concept = input_array[0];
	i1 = input_array[1];
	i2 = input_array[2];
	i3 = input_array[3];
	i4 = input_array[4];
	n_f_th = input_array[5];

	// number of deposits:
	int n = static_cast<int> (x[0].value());
	int value;

	vector<int> input;
	for (int i = 0; i < 5; ++i)
	{
		if (i < (n + 1)) {
			value = static_cast<int> (x[i + 1].value()); // get input vector
		}
		else {
			value = -1;
		}
		input.push_back(value);
	}

	print_vector(input);

	// number of branches
	size_t k = n_f_th.size();

	// Look up safety factor value
	vector<int> lookup;
    
    bool found = false;
	for (int i = 0; i < k; ++i)
	{
		lookup = { static_cast<int> (concept[i]), static_cast<int> (i1[i]),
			static_cast<int> (i2[i]), static_cast<int> (i3[i]),
			static_cast<int> (i4[i]) };

		if (input == lookup) {
			f = -n_f_th[i];
			x.set_bb_output(0, f);
			count_eval = true;
            found = true;
			//cout << "objective: " << f << endl;
			// terminate the loop
			break;
		}
	}
    if ( !found )
    {
        x.set_bb_output(0,NOMAD::INF);
		//cout << "objective: " << f << endl;
        count_eval = true;
    }
	return true;
}

/*-----------------------------------------*/
/*  constructor: creates the 4 signatures  */
/*-----------------------------------------*/
My_Extended_Poll::My_Extended_Poll(NOMAD::Parameters & p)
	: Extended_Poll(p),
	_s1(NULL),
	_s2(NULL),
	_s3(NULL),
	_s4(NULL)
{
	// signature for 1 asset:
	// ----------------------
	vector<NOMAD::bb_input_type> bbit_1(3);
	bbit_1[0] = NOMAD::CATEGORICAL;
	bbit_1[1] = bbit_1[2] = NOMAD::INTEGER;

	const NOMAD::Point & d0_1 = p.get_initial_poll_size();
	const NOMAD::Point & lb_1 = p.get_lb();
	const NOMAD::Point & ub_1 = p.get_ub();

	_s1 = new NOMAD::Signature(3,
		bbit_1,
		d0_1,
		lb_1,
		ub_1,
		p.get_direction_types(),
		p.get_sec_poll_dir_types(),
		p.get_int_poll_dir_types(),
		_p.out());

	// signature for 2 deposits:
	// -----------------------
	{
	vector<NOMAD::bb_input_type> bbit_2(4);
	bbit_2[0] = NOMAD::CATEGORICAL;
	bbit_2[1] = bbit_2[2] = bbit_2[3] = NOMAD::INTEGER;

	NOMAD::Point d0_2(4);
	NOMAD::Point lb_2(4);
	NOMAD::Point ub_2(4);

	// Categorical variables don't need bounds
	for (int i = 0; i < 4; ++i)
	{
		if (i == 0) {
			bbit_2[i] = bbit_1[0];
			d0_2[i] = d0_1[0];
			lb_2[i] = lb_1[0];
			ub_2[i] = ub_1[0];
		}
		else if (i == 1) {
			bbit_2[i] = bbit_1[1];
			d0_2[i] = d0_1[1];
			lb_2[i] = lb_1[1];
			ub_2[i] = ub_1[1];
		}
		else {
			bbit_2[i] = bbit_1[2];
			d0_2[i] = d0_1[2];
			lb_2[i] = lb_1[2];
			ub_2[i] = ub_1[2];
		}
	}

	_s2 = new NOMAD::Signature(4,
		bbit_2,
		d0_2,
		lb_2,
		ub_2,
		p.get_direction_types(),
		p.get_sec_poll_dir_types(),
		p.get_int_poll_dir_types(),
		_p.out());
	}
	// signature for 3 deposits:
	// -----------------------
	{
		vector<NOMAD::bb_input_type> bbit_3(5);
		bbit_3[0] = NOMAD::CATEGORICAL;
		bbit_3[1] = bbit_3[2] = bbit_3[3] = bbit_3[4] = NOMAD::INTEGER;

		NOMAD::Point d0_3(5);
		NOMAD::Point lb_3(5);
		NOMAD::Point ub_3(5);

		// Categorical variables don't need bounds
		for (int i = 0; i < 5; ++i)
		{
			if (i == 0) {
				bbit_3[i] = bbit_1[0];
				d0_3[i] = d0_1[0];
				lb_3[i] = lb_1[0];
				ub_3[i] = ub_1[0];
			}
			else if (i == 1) {
				bbit_3[i] = bbit_1[1];
				d0_3[i] = d0_1[1];
				lb_3[i] = lb_1[1];
				ub_3[i] = ub_1[1];
			}
			else {
				bbit_3[i] = bbit_1[2];
				d0_3[i] = d0_1[2];
				lb_3[i] = lb_1[2];
				ub_3[i] = ub_1[2];
			}
		}

		_s3 = new NOMAD::Signature(5,
			bbit_3,
			d0_3,
			lb_3,
			ub_3,
			p.get_direction_types(),
			p.get_sec_poll_dir_types(),
			p.get_int_poll_dir_types(),
			_p.out());
	}
	// signature for 4 deposits:
	// -----------------------
	{
		vector<NOMAD::bb_input_type> bbit_4(6);
		bbit_4[0] = NOMAD::CATEGORICAL;
		bbit_4[1] = bbit_4[2] = bbit_4[3] = bbit_4[4] = bbit_4[5] = NOMAD::INTEGER;

		NOMAD::Point d0_4(6);
		NOMAD::Point lb_4(6);
		NOMAD::Point ub_4(6);

		// Categorical variables don't need bounds
		for (int i = 0; i < 6; ++i)
		{
			if (i == 0) {
				bbit_4[i] = bbit_1[0];
				d0_4[i] = d0_1[0];
				lb_4[i] = lb_1[0];
				ub_4[i] = ub_1[0];
			}
			else if (i == 1) {
				bbit_4[i] = bbit_1[1];
				d0_4[i] = d0_1[1];
				lb_4[i] = lb_1[1];
				ub_4[i] = ub_1[1];
			}
			else {
				bbit_4[i] = bbit_1[2];
				d0_4[i] = d0_1[2];
				lb_4[i] = lb_1[2];
				ub_4[i] = ub_1[2];
			}
		}

		_s4 = new NOMAD::Signature(6,
			bbit_4,
			d0_4,
			lb_4,
			ub_4,
			p.get_direction_types(),
			p.get_sec_poll_dir_types(),
			p.get_int_poll_dir_types(),
			_p.out());

	}
}

/*--------------------------------------*/
/*  construct the extended poll points  */
/*      (categorical neighborhoods)     */
/*--------------------------------------*/
void My_Extended_Poll::construct_extended_points(const NOMAD::Eval_Point & x) {

	// number of deposits:
	int n = static_cast<int> (x[0].value());
	vector<NOMAD::Point> extended;
	// 1 deposit:
	// --------
	if (n == 1) {

		// current type of deposit
		int cur_type = static_cast<int> (x[2].value());

		// current type of concept:
		int c = static_cast<int> (x[1].value());

		// list of concepts
		vector<int> concepts = { 0,1 };

		// this vector contains the types of the other deposits:
		vector<int> other_types_c0, other_types_c1, other_types, other_concepts;

		switch (cur_type) {
		case 0:
			other_types_c0.push_back(1);

			other_types_c1.push_back(1);
			other_types_c1.push_back(2);
			other_types_c1.push_back(3);
			break;
		case 1:
			other_types_c0.push_back(0);

			other_types_c1.push_back(0);
			other_types_c1.push_back(2);
			other_types_c1.push_back(3);
			break;
		case 2:
			other_types_c1.push_back(0);
			other_types_c1.push_back(1);
			other_types_c1.push_back(3);
			break;
		case 3:
			other_types_c1.push_back(0);
			other_types_c1.push_back(1);
			other_types_c1.push_back(2);
			break;
		}

		// types of deposits available to each concept
		switch (c) {
		case 0:
			other_concepts.push_back(1);
			other_types = other_types_c0;
			break;
		case 1:
			other_concepts.push_back(0);
			other_types = other_types_c1;
			break;
		}

		// add 1 deposit (1 or 3 neighbors):
		for (size_t k = 0; k < other_types.size(); ++k) {
			NOMAD::Point y(4);

			y[0] = 2;
			y[1] = c;
			y[2] = cur_type;
			y[3] = other_types[k];

			add_extended_poll_point(y, *_s2);
			extended.push_back(y);
		}

		// change the type of the deposit to the other types (1 or 3 neighbors):
		for (size_t k = 0; k < other_types.size(); ++k)
		{
			NOMAD::Point y = x;
			y[2] = other_types[k];

			add_extended_poll_point(y, *_s1);
			extended.push_back(y);
		}

		// loop over concepts
		if (x[2] == 0 || x[2] == 1) { // change concept allowed
			for (size_t j = 0; j < other_concepts.size(); ++j) {

				switch (other_concepts[j]) {
				case 0:
					other_types = { 0,1 };
					break;
				case 1:
					other_types = { 0,1,2,3 };
					break;
				}

				// change the type of the deposit to the other types (1 or 3 neighbors):
				for (size_t k = 0; k < other_types.size(); ++k)
				{
					NOMAD::Point y = x;
					y[1] = other_concepts[j];
					y[2] = other_types[k];

					add_extended_poll_point(y, *_s1);
					extended.push_back(y);
				}

			}
		}

	}

	// 2 deposits:
	// --------
	else if (n == 2) {

		vector<int> deposits = { 0,1,2,3 };
		vector<int> other_types;
		deposits.erase(remove(deposits.begin(), deposits.end(), x[2]), deposits.end());
		deposits.erase(remove(deposits.begin(), deposits.end(), x[3]), deposits.end());
		other_types = deposits;

		// current type of deposit
		int cur_type = static_cast<int> (x[3].value());

		// current type of concept:
		int c = static_cast<int> (x[1].value());

		// remove 1 deposit (1 neighbor):
		{
			NOMAD::Point y(3);
			y[0] = 1;
			y[1] = c;
			y[2] = x[2];

			add_extended_poll_point(y, *_s1);
			extended.push_back(y);
		}

		if (c == 1) {
			// change the type of one deposit (2 neighbors):
			for (size_t k = 0; k < other_types.size(); ++k)
			{
				NOMAD::Point y = x;
				y[3] = other_types[k];

				add_extended_poll_point(y, *_s2);
				extended.push_back(y);
			}

			// add one deposit (2 neighbors):
			for (size_t k = 0; k < other_types.size(); ++k)
			{
				NOMAD::Point y(5);
				y[0] = 3;
				y[1] = c;
				y[2] = x[2];
				y[3] = cur_type;
				y[4] = other_types[k];

				add_extended_poll_point(y, *_s3);
				extended.push_back(y);
			}
		}



	}

	// 3 deposits:
	// ---------
	else if (n == 3)
	{

		vector<int> deposits = { 0,1,2,3 };
		vector<int> other_types;
		deposits.erase(remove(deposits.begin(), deposits.end(), x[2]), deposits.end());
		deposits.erase(remove(deposits.begin(), deposits.end(), x[3]), deposits.end());
		deposits.erase(remove(deposits.begin(), deposits.end(), x[4]), deposits.end());
		other_types = deposits;

		// current type of deposit
		int cur_type = static_cast<int> (x[4].value());

		// current type of concept:
		int c = static_cast<int> (x[1].value());

		// remove 1 deposit (1 neighbor):
		{
			NOMAD::Point y(4);
			y[0] = 2;
			y[1] = c;
			y[2] = x[2];
			y[3] = x[3];

			add_extended_poll_point(y, *_s2);
			extended.push_back(y);
		}

		// change the type of one deposit (1 neighbor):
		for (size_t k = 0; k < other_types.size(); ++k)
		{
			NOMAD::Point y = x;
			y[4] = other_types[k];

			add_extended_poll_point(y, *_s3);
			extended.push_back(y);
		}

		// add one deposit (1 neighbor):
		for (size_t k = 0; k < other_types.size(); ++k)
		{
			NOMAD::Point y(6);
			y[0] = 4;
			y[1] = c;
			y[2] = x[2];
			y[3] = x[3];
			y[4] = cur_type;
			y[5] = other_types[k];

			add_extended_poll_point(y, *_s4);
			extended.push_back(y);
		}

	}

	// 4 deposits:
	// ---------
	else {
		// current type of deposit
		int cur_type = static_cast<int> (x[5].value());

		// current type of concept:
		int c = static_cast<int> (x[1].value());

		// remove one deposit (1 neighbor):
		NOMAD::Point y(5);
		y[0] = 3;
		y[1] = c;
		y[2] = x[2];
		y[3] = x[3];
		y[4] = x[4];

		add_extended_poll_point(y, *_s3);
		extended.push_back(y);
	}

	//for (size_t k = 0; k < extended.size(); k++) {

	//	NOMAD::Point p = extended[k];
	//	cout << p << endl;

	//}

}